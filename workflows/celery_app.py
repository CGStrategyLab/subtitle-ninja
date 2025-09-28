import os
from celery import Celery

# Celery configuration
redis_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')

celery_app = Celery(
    'subtitle_ninja',
    broker=redis_url,
    backend=redis_url,
    include=['workflows.celery_app']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

def update_job_status_redis(job_id: str, status: str, progress: int = None, message: str = None,
                           output_file: str = None, error: str = None):
    """Update job status in Redis"""
    import redis
    import json

    redis_client = redis.Redis.from_url(redis_url)

    # Get existing status or create new
    try:
        existing = redis_client.get(f"job:{job_id}")
        job_data = json.loads(existing) if existing else {}
    except:
        job_data = {}

    # Update fields
    job_data["status"] = status
    if progress is not None:
        job_data["progress"] = progress
    if message is not None:
        job_data["message"] = message
    if output_file is not None:
        job_data["output_file"] = output_file
    if error is not None:
        job_data["error"] = error

    # Save to Redis
    redis_client.set(f"job:{job_id}", json.dumps(job_data), ex=3600)  # Expire in 1 hour

@celery_app.task(bind=True)
def process_video_task(self, job_id: str, input_path: str, style_preset: str = "instagram_classic"):
    """Process video with subtitles using Celery task with style selection"""
    from workflows.process_video import VideoProcessor

    try:
        # Update status to processing
        update_job_status_redis(job_id, "processing", 10, f"Starting video processing with {style_preset} style...")

        # Initialize processor
        processor = VideoProcessor(job_id)

        # Process the video with selected style
        output_path = processor.process(input_path, style_preset, progress_callback=lambda p, msg:
            update_job_status_redis(job_id, "processing", p, msg))

        # Update final status
        output_filename = os.path.basename(output_path)
        update_job_status_redis(job_id, "completed", 100, "Video processing completed!", output_filename)

        return {"status": "completed", "output_file": output_filename}

    except Exception as e:
        error_msg = str(e)
        update_job_status_redis(job_id, "failed", 0, "Processing failed", error=error_msg)
        raise self.retry(exc=e, countdown=60, max_retries=3)