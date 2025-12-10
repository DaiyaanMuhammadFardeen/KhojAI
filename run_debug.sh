#!/bin/bash

# Run Flutter app in debug mode with detailed logging
cd /home/daiyaan2002/Desktop/Projects/KhojAI/mobile_application

echo "Starting KhojAI in debug mode..."
echo "==============================================="
echo "Watch the console output carefully for any errors"
echo "The app should NOT crash when loading conversations"
echo "==============================================="
echo ""

# Run with verbose logging
flutter run -d linux -v 2>&1 | tee flutter_run.log

# Show any errors at the end
echo ""
echo "==============================================="
echo "Checking for ERRORS in the output..."
echo "==============================================="
grep -i "error\|exception\|crash" flutter_run.log | head -20
