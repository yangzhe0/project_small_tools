param(
  [int]$Port = 8080
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootPath = [System.IO.Path]::GetFullPath($root)
$listener = [System.Net.HttpListener]::new()
$prefix = "http://localhost:$Port/"

$contentTypes = @{
  ".css"  = "text/css; charset=utf-8"
  ".html" = "text/html; charset=utf-8"
  ".js"   = "text/javascript; charset=utf-8"
  ".json" = "application/json; charset=utf-8"
  ".png"  = "image/png"
  ".svg"  = "image/svg+xml"
  ".txt"  = "text/plain; charset=utf-8"
}

function Write-Response {
  param(
    [Parameter(Mandatory = $true)]
    [System.Net.HttpListenerContext]$Context,

    [Parameter(Mandatory = $true)]
    [int]$StatusCode,

    [Parameter(Mandatory = $true)]
    [string]$Body,

    [string]$ContentType = "text/plain; charset=utf-8"
  )

  $bytes = [System.Text.Encoding]::UTF8.GetBytes($Body)
  $Context.Response.StatusCode = $StatusCode
  $Context.Response.ContentType = $ContentType
  $Context.Response.ContentLength64 = $bytes.Length
  $Context.Response.OutputStream.Write($bytes, 0, $bytes.Length)
  $Context.Response.OutputStream.Close()
}

$listener.Prefixes.Add($prefix)
$listener.Start()

Write-Host ""
Write-Host "Smile Detector Mini is running at $prefix" -ForegroundColor Green
Write-Host "Open the URL in Chrome or Edge and allow camera access." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host ""

try {
  while ($listener.IsListening) {
    $context = $listener.GetContext()
    $requestPath = [Uri]::UnescapeDataString($context.Request.Url.AbsolutePath.TrimStart('/'))

    if ([string]::IsNullOrWhiteSpace($requestPath)) {
      $requestPath = "index.html"
    }

    $fullPath = [System.IO.Path]::GetFullPath((Join-Path $rootPath $requestPath))

    if (-not $fullPath.StartsWith($rootPath, [System.StringComparison]::OrdinalIgnoreCase)) {
      Write-Response -Context $context -StatusCode 403 -Body "Forbidden"
      continue
    }

    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
      Write-Response -Context $context -StatusCode 404 -Body "Not Found"
      continue
    }

    $extension = [System.IO.Path]::GetExtension($fullPath).ToLowerInvariant()
    $contentType = $contentTypes[$extension]
    if (-not $contentType) {
      $contentType = "application/octet-stream"
    }

    $bytes = [System.IO.File]::ReadAllBytes($fullPath)
    $context.Response.StatusCode = 200
    $context.Response.ContentType = $contentType
    $context.Response.ContentLength64 = $bytes.Length
    $context.Response.OutputStream.Write($bytes, 0, $bytes.Length)
    $context.Response.OutputStream.Close()
  }
} finally {
  $listener.Stop()
  $listener.Close()
}
