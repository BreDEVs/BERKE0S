#!/bin/bash

# BERKE0S Display Test Script
# Test display configuration and compatibility

echo "BERKE0S Display Test Script"
echo "=========================="
echo ""

# Test X server availability
echo "1. Testing X server availability..."
if command -v X >/dev/null 2>&1; then
    echo "   ✓ X server binary found: $(which X)"
else
    echo "   ✗ X server binary not found"
fi

if command -v Xorg >/dev/null 2>&1; then
    echo "   ✓ Xorg binary found: $(which Xorg)"
else
    echo "   ✗ Xorg binary not found"
fi

# Test display environment
echo ""
echo "2. Testing display environment..."
if [ -n "$DISPLAY" ]; then
    echo "   ✓ DISPLAY variable set: $DISPLAY"
    
    # Test X connection
    if xdpyinfo >/dev/null 2>&1; then
        echo "   ✓ X server connection successful"
    else
        echo "   ✗ X server connection failed"
    fi
else
    echo "   ✗ DISPLAY variable not set"
fi

# Test Tkinter
echo ""
echo "3. Testing Python Tkinter..."
if python3 -c "import tkinter; tkinter.Tk().withdraw()" >/dev/null 2>&1; then
    echo "   ✓ Tkinter working correctly"
else
    echo "   ✗ Tkinter not working"
fi

# Test window manager
echo ""
echo "4. Testing window managers..."
for wm in flwm jwm openbox icewm twm; do
    if command -v $wm >/dev/null 2>&1; then
        echo "   ✓ Window manager available: $wm"
    fi
done

# Test graphics info
echo ""
echo "5. Graphics information..."
if command -v lspci >/dev/null 2>&1; then
    echo "   Graphics hardware:"
    lspci | grep -i vga | sed 's/^/     /'
fi

echo ""
echo "Test completed."