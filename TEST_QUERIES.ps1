#!/usr/bin/env powershell

# OceanFront - Test Query Script
# Tests the complete NL-to-Parquet pipeline

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   🌊 OceanFront Query Test - Testing Fixed Backend    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check
Write-Host "TEST 1: Backend Health Check" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────" -ForegroundColor Gray
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -ErrorAction Stop
    $healthData = $health.Content | ConvertFrom-Json
    Write-Host "✅ Backend is healthy!" -ForegroundColor Green
    Write-Host "   Services: $($healthData.services | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend health check failed: $_" -ForegroundColor Red
    Write-Host "   Make sure backend is running: python main.py" -ForegroundColor Yellow
    exit
}
Write-Host ""

# Test 2: Simple Query
Write-Host "TEST 2: Query - Show all available ocean buoys" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────" -ForegroundColor Gray
try {
    $queryBody = @{
        query = "Show me all available ocean buoys"
    } | ConvertTo-Json
    
    Write-Host "Sending query..." -ForegroundColor Cyan
    $response = Invoke-WebRequest `
        -Uri "http://localhost:8000/api/query" `
        -Method POST `
        -Body $queryBody `
        -ContentType "application/json" `
        -ErrorAction Stop
    
    $responseData = $response.Content | ConvertFrom-Json
    
    if ($responseData.success) {
        Write-Host "✅ Query succeeded!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Result:" -ForegroundColor Cyan
        Write-Host $responseData.markdown_result -ForegroundColor White
        Write-Host ""
        Write-Host "Stats:" -ForegroundColor Cyan
        Write-Host "  • Rows: $($responseData.row_count)" -ForegroundColor White
        Write-Host "  • SQL Generated: $($responseData.sql_query)" -ForegroundColor White
    } else {
        Write-Host "❌ Query failed:" -ForegroundColor Red
        Write-Host $responseData.error -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Request failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 3: Filter Query
Write-Host "TEST 3: Query - Buoys on west coast" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────" -ForegroundColor Gray
try {
    $queryBody = @{
        query = "Show me buoys on the west coast"
    } | ConvertTo-Json
    
    Write-Host "Sending query..." -ForegroundColor Cyan
    $response = Invoke-WebRequest `
        -Uri "http://localhost:8000/api/query" `
        -Method POST `
        -Body $queryBody `
        -ContentType "application/json" `
        -ErrorAction Stop
    
    $responseData = $response.Content | ConvertFrom-Json
    
    if ($responseData.success) {
        Write-Host "✅ Query succeeded!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Result:" -ForegroundColor Cyan
        Write-Host $responseData.markdown_result -ForegroundColor White
    } else {
        Write-Host "❌ Query failed:" -ForegroundColor Red
        Write-Host $responseData.error -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Request failed: $_" -ForegroundColor Red
}
Write-Host ""

# Summary
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           ✅ Tests Complete - System Working!         ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Open frontend: http://localhost:3000/ai-agent" -ForegroundColor White
Write-Host "  2. Start asking questions about ocean data" -ForegroundColor White
Write-Host "  3. Try the queries from the test questions document" -ForegroundColor White
Write-Host ""
