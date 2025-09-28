# 🤝 Contributing to Subtitle Ninja

Thank you for your interest in contributing to Subtitle Ninja! This project showcases modern AI-powered workflow automation patterns and welcomes contributions from developers of all skill levels.

## 🎯 Project Vision

Subtitle Ninja demonstrates practical implementation of:
- **AI-powered video processing** with OpenAI Whisper
- **Microservices architecture** using Docker Compose
- **Real-time job processing** with Celery and Redis
- **Professional subtitle styling** with Advanced SubStation Alpha (ASS)
- **Modern web development** with FastAPI and responsive JavaScript

## 🚀 Quick Setup for Contributors

### Prerequisites
- **Docker & Docker Compose** ([Installation Guide](https://docs.docker.com/get-docker/))
- **Git** for version control
- **Python 3.12+** (for local development)
- **Node.js** (optional, for frontend tooling)

### Development Environment

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/subtitle-ninja.git
   cd subtitle-ninja
   ```

2. **Start development environment**
   ```bash
   # Start all services with hot reload
   docker-compose up --build

   # Or for background processing
   docker-compose up --build -d
   ```

3. **Access the application**
   - **Web Interface**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **MinIO Console**: http://localhost:9001 (admin/admin)

## 📁 Project Structure

```
subtitle-ninja/
├── 📁 api/                     # FastAPI backend
│   ├── main.py                # API endpoints and routes
│   └── __init__.py
├── 📁 workflows/               # Processing pipeline
│   ├── process_video.py       # Core video processing logic
│   ├── style_config.py        # Subtitle styling presets
│   ├── ass_renderer.py        # Advanced subtitle rendering
│   ├── celery_app.py          # Async job processing
│   └── __init__.py
├── 📁 static/                  # Frontend assets
│   ├── index.html             # Main web interface
│   └── app.js                 # JavaScript for upload/progress
├── 📁 docs/                    # Documentation
├── 🐳 docker-compose.yml       # Service orchestration
├── 🐳 Dockerfile              # Container definition
├── 📄 pyproject.toml          # Python dependencies
└── 📄 requirements.txt        # Fallback dependencies
```

## 🎨 Areas for Contribution

### 🌟 **High Impact Contributions**

#### 1. **New Subtitle Styling Presets**
Create new professional styling options in `workflows/style_config.py`:

```python
"custom_style": {
    "name": "Custom Style Name",
    "description": "Brief description for users",
    "font_family": "Arial Black",
    "font_size": "dynamic",  # or specific size
    "primary_color": "#FFFFFF",
    "highlight_color": "#FF6B6B",
    "outline_color": "#000000",
    "glow_color": "rgba(255,107,107,0.8)",
    "position": "bottom_center",
    "animations": {
        "word_highlight": True,
        "fade_in": True,
        "scale_effect": 1.1
    }
}
```

#### 2. **Performance Optimizations**
- GPU acceleration for video processing
- Parallel processing for multiple videos
- Memory optimization for large files
- Caching strategies for repeated operations

#### 3. **Frontend Enhancements**
- Style preview thumbnails
- Drag-and-drop improvements
- Mobile responsiveness
- Progress visualization enhancements

#### 4. **API Extensions**
- Batch processing endpoints
- Webhook notifications
- Custom styling API
- Health check improvements

### 🔧 **Technical Improvements**

#### 5. **Code Quality & Testing**
- Unit tests for video processing
- Integration tests for API endpoints
- Performance benchmarking
- Error handling improvements

#### 6. **Documentation**
- API documentation improvements
- Video tutorials
- Architecture diagrams
- Troubleshooting guides

## 🛠️ Development Guidelines

### **Code Style**
- **Python**: Follow PEP 8, use type hints
- **JavaScript**: Use modern ES6+ syntax
- **Comments**: Focus on why, not what
- **Naming**: Use descriptive, clear names

### **Commit Messages**
Use conventional commit format:
```
feat: add new TikTok style preset with neon effects
fix: resolve memory leak in video processing
docs: update API documentation for /styles endpoint
refactor: simplify subtitle positioning logic
```

### **Pull Request Process**

1. **Create feature branch**
   ```bash
   git checkout -b feature/amazing-new-feature
   ```

2. **Make your changes**
   - Keep commits focused and atomic
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Test with Docker
   docker-compose up --build

   # Run tests (when available)
   docker-compose exec web-api pytest
   ```

4. **Submit PR with description**
   - Clear title and description
   - Reference any related issues
   - Include screenshots for UI changes
   - List breaking changes (if any)

## 🧪 Testing Guidelines

### **Manual Testing**
Before submitting, test with:
- **Various video formats**: MP4, AVI, MOV, MKV
- **Different aspect ratios**: 16:9, 9:16, 1:1
- **Various file sizes**: Small (< 10MB) to large (> 100MB)
- **Multiple browsers**: Chrome, Firefox, Safari, Edge

### **Performance Testing**
- Process videos of different lengths
- Monitor memory usage during processing
- Test concurrent uploads
- Verify cleanup of temporary files

## 🎯 Feature Request Process

### **Before Submitting**
1. Check existing issues and discussions
2. Consider if it aligns with project goals
3. Think about implementation complexity
4. Consider backward compatibility

### **Submission Template**
```markdown
## Feature Description
Brief description of the proposed feature

## Use Case
Who would benefit and how?

## Implementation Ideas
High-level approach or technical considerations

## Alternatives Considered
Other solutions you've thought about
```

## 🐛 Bug Report Process

### **Bug Report Template**
```markdown
## Bug Description
Clear description of what went wrong

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should have happened

## Actual Behavior
What actually happened

## Environment
- OS: [Windows/Mac/Linux]
- Browser: [Chrome/Firefox/Safari]
- Docker version: [version]
- Video format: [MP4/AVI/etc]
- File size: [approximate size]

## Additional Context
Logs, screenshots, or other relevant information
```

## 📖 Learning Resources

To better understand the technologies used in this project:

### **AI & Video Processing**
- **[CG Strategy Lab](https://cgstrategylab.com)** - AI implementation strategies and workflow automation
- **[OpenAI Whisper Documentation](https://github.com/openai/whisper)** - Speech recognition API
- **[FFmpeg Documentation](https://ffmpeg.org/documentation.html)** - Video processing tools

### **Backend Development**
- **[FastAPI Documentation](https://fastapi.tiangolo.com/)** - Modern Python web framework
- **[Celery Documentation](https://docs.celeryq.dev/)** - Distributed task queue
- **[Redis Documentation](https://redis.io/documentation)** - In-memory data structure store

### **DevOps & Containerization**
- **[Docker Compose Guide](https://docs.docker.com/compose/)** - Multi-container applications
- **[MinIO Documentation](https://docs.min.io/)** - S3-compatible object storage

## 🏆 Recognition

Contributors will be recognized in:
- README.md acknowledgments
- Release notes for significant contributions
- Project documentation
- Social media shoutouts (with permission)

## 📞 Getting Help

- **Discord/Slack**: [Coming soon - community chat]
- **GitHub Discussions**: For questions and ideas
- **GitHub Issues**: For bugs and feature requests
- **Documentation**: Check docs/ folder for guides

## 🤖 AI-Powered Development

This project embraces AI-assisted development. Feel free to use AI tools for:
- Code generation and optimization
- Documentation writing
- Test case creation
- Architecture planning

For insights on AI-powered development workflows, check out [CG Strategy Lab's AI Agent Frameworks](https://cgstrategylab.com/ai-agent-frameworks).

---

## 📄 License

By contributing to Subtitle Ninja, you agree that your contributions will be licensed under the MIT License.

---

<div align="center">

**Thank you for contributing to Subtitle Ninja!** 🎬

*Together, we're building the future of AI-powered video processing*

</div>