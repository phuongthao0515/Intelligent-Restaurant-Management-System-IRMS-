#!/bin/bash

echo "🚀 Setting up IRMS Frontend Order..."

# go to frontend (create if not exist)
cd frontend-order

# check if already initialized
if [ ! -f "package.json" ]; then
  echo "📦 Initializing Vite React app..."

  npm create vite@latest . -- --template react
else
  echo "📁 Existing project detected, skipping init..."
fi

echo "📦 Installing dependencies..."
npm install

echo "📦 Installing libraries..."
npm install react-router-dom react-icons

echo "✅ Setup complete!"

echo ""
echo "👉 Run the project:"
echo "cd frontend-order"
echo "npm run dev"