param (
    [Parameter(Mandatory=$true)]
    [ValidateScript({ try { $_ | ConvertFrom-Json; $true } catch { $false } })]
    [string]$dataJson,

    [Parameter()]
    [ValidateScript({ Test-Path -Path (Split-Path $_ -Parent) })]
    [string]$dir = ".\.cache"
)

# Ensure the directory exists
if (-not (Test-Path -Path $dir)) {
    try {
        New-Item -ItemType Directory -Path $dir -ErrorAction Stop | Out-Null
    } catch {
        Write-Error "Failed to create directory: $dir"
        exit 1
    }
}

try {
    $rawJson = $dataJson | ConvertFrom-Json
} catch {
    Write-Error "Invalid JSON format."
    exit 1
}

# Validate JSON structure
if (-not $rawJson.PSObject.Properties.Match("URL") -or
    -not $rawJson.PSObject.Properties.Match("Method") -or
    -not $rawJson.PSObject.Properties.Match("Headers")) {
    Write-Error "Invalid JSON structure. Required properties: URL, Method, Headers."
    exit 1
}

# Calculate hash from the JSON string
$utfEncoding = [System.Text.Encoding]::UTF8
$sha256 = [System.Security.Cryptography.SHA256]::Create()

$hashBytes = $sha256.ComputeHash($utfEncoding.GetBytes($dataJson))
$hash = [BitConverter]::ToString($hashBytes).Replace("-", "").ToLower()

$dumpPath = Join-Path -Path $dir -ChildPath "$hash.json"

# Prepare headers
$headers = @{}
$rawJson.Headers.psobject.Properties | ForEach-Object {
    $headers[$_.Name] = $_.Value
}

try {
    if ($rawJson.Method -eq "GET") {
        $response = Invoke-WebRequest -Uri $rawJson.URL -Headers $headers -Method $rawJson.Method
    } else {
        $body = $utfEncoding.GetBytes(($rawJson.Body | ConvertTo-Json -Compress))
        $response = Invoke-WebRequest -Uri $rawJson.URL -Headers $headers -Method $rawJson.Method -Body $body
    }

    # Check PowerShell version
    if ($PSVersionTable.PSVersion.Major -lt 6) {
        # Convert response content from ISO-8859-1 to UTF-8 for legacy versions
        $responseContent = $utfEncoding.GetString([System.Text.Encoding]::GetEncoding("ISO-8859-1").GetBytes($response.Content))
        $responseContent | Out-File -FilePath $dumpPath -Encoding utf8

        # Output response content
        Write-Output $responseContent

    } else {
        # Directly save response content for newer versions
        $response.Content | Out-File -FilePath $dumpPath -Encoding utf8

        # Output response content
        Write-Output $response.Content
    }

} catch {
    Write-Error "Failed to make the web request: $_"
}