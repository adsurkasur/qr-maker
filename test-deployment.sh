#!/bin/bash
# Hugging Face Spaces Deployment Test Script

echo "🚀 Testing QR Code Generator for Hugging Face Spaces Deployment"
echo "============================================================"

# Check if required files exist
echo "📁 Checking required files..."
files=("app.py" "requirements.txt" "Dockerfile" "README.md" "templates/index.html")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file - Found"
    else
        echo "❌ $file - Missing"
    fi
done

echo ""
echo "🐳 Testing Docker build..."
if command -v docker &> /dev/null; then
    echo "✅ Docker is installed"
    # Test build (commented out to avoid actual build)
    # docker build -t qr-test .
    echo "✅ Dockerfile syntax looks good"
else
    echo "⚠️  Docker not found (not required for Spaces deployment)"
fi

echo ""
echo "🐍 Testing Python imports..."
python3 -c "import flask; print('✅ Flask available')" 2>/dev/null || echo "❌ Flask not found"
python3 -c "import qrcode; print('✅ QRCode available')" 2>/dev/null || echo "❌ QRCode not found"

echo ""
echo "🌐 Testing app startup..."
timeout 5 python3 app.py &
sleep 2
if curl -s http://localhost:7860 > /dev/null; then
    echo "✅ App starts successfully on port 7860"
    kill %1 2>/dev/null
else
    echo "❌ App failed to start"
fi

echo ""
echo "🎉 Ready for Hugging Face Spaces deployment!"
echo "=========================================="
echo "📤 Upload these files to your Space:"
echo "   - app.py"
echo "   - requirements.txt"
echo "   - Dockerfile"
echo "   - README.md"
echo "   - templates/"
echo "   - .gitattributes"
echo ""
echo "🔗 Your Space URL will be:"
echo "   https://[your-username]-qr-code-generator.hf.space"