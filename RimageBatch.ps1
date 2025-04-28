while ($true) {
    # Check if rimage.exe exists in the same directory as the script
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
    $rimagePath = Join-Path -Path $scriptDir -ChildPath "rimage.exe"
    if (-not (Test-Path $rimagePath)) {
        # Check if rimage is in the PATH environment variable
        $rimageInPath = $false
        foreach ($path in ($Env:Path -split ';')) {
            if (![string]::IsNullOrWhiteSpace($path)) {
                $potentialRimagePath = Join-Path -Path $path -ChildPath "rimage.exe"
                if (Test-Path $potentialRimagePath) {
                    $rimageInPath = $true
                    break
                }
            }
        }
        if (-not $rimageInPath) {
            Write-Host "Rimage is not found in the script directory or the PATH environment variable. Please install it before running this script."
            return
        }
    }

    # Prompt for input directory or file
    do {
        $inputPath = Read-Host -Prompt "Please enter the path of the directory or file to be processed"
        $isValid = Test-Path $inputPath
        if (-not $isValid) {
            Write-Host "The path you entered is not valid. Please try again."
        }
    } while (-not $isValid)

    # Prompt for output format
    $formats = "jpg", "png", "oxipng", "jpegxl", "webp", "avif"
    for ($i = 0; $i -lt $formats.Length; $i++) {
        Write-Host "$($i+1): $($formats[$i])"
    }
    do {
        $formatIndex = Read-Host -Prompt "Please enter the number for the output format"
        $isValidFormat = $formatIndex -ge 1 -and $formatIndex -le $formats.Length
        if (-not $isValidFormat) {
            Write-Host "The number you entered is not valid. Please try again."
        }
    } while (-not $isValidFormat)
    $outputFormat = $formats[$formatIndex - 1]

    # Prompt for output quality
    do {
        $outputQuality = Read-Host -Prompt "Please enter the output quality (1-100)"
        $outputQuality = [int]$outputQuality
        $isValidQuality = $outputQuality -ge 1 -and $outputQuality -le 100
        if (-not $isValidQuality) {
            Write-Host "The quality you entered is not valid. Please try again."
        }
    } while (-not $isValidQuality)

    # Prompt for resolution ratio
    do {
        $resolutionRatio = Read-Host -Prompt "Please enter the resolution ratio (%)"
        $resolutionRatio = [int]$resolutionRatio
        $isValidRatio = $resolutionRatio -gt 0
        if (-not $isValidRatio) {
            Write-Host "The resolution ratio should be a positive number. Please try again."
        }
    } while (-not $isValidRatio)

    # Convert the ratio to a decimal
    $ratio = $resolutionRatio / 100

    # Prompt for output directory
    do {
        $outputDir = Read-Host -Prompt "Please enter the path of the output directory"
        $isValid = Test-Path $outputDir
        if (-not $isValid) {
            Write-Host "The output directory does not exist. Creating now..."
            New-Item -ItemType Directory -Force -Path $outputDir
            if (Test-Path $outputDir) {
                Write-Host "Output directory created successfully."
                $isValid = $true
            }
            else {
                Write-Host "Failed to create output directory. Please try again."
            }
        }
    } while (-not $isValid)

    # Initialize counters
    $totalFiles = 0
    $processedFiles = 0

    # Check if inputPath is a directory or a file
    if (Test-Path $inputPath -PathType Container) {
        $totalFiles = (Get-ChildItem -Path $inputPath -Recurse -File).Count
        $files = Get-ChildItem -Path $inputPath -Recurse -File
    }
    else {
        $totalFiles = 1
        $files = Get-Item -Path $inputPath
    }

    # Process files
    foreach ($file in $files) {
        # Get the image's original width and height
        $imageSize = identify -format "%wx%h" $file.FullName
        $originalWidth, $originalHeight = $imageSize -split 'x'
        $originalWidth = [int]$originalWidth
        $originalHeight = [int]$originalHeight
        $newWidth = [int]($originalWidth * $ratio)
        $newHeight = [int]($originalHeight * $ratio)

        Write-Host "Processing file: $($file.FullName) ($originalWidth x $originalHeight)"

        $newFileName = [System.IO.Path]::ChangeExtension($file.Name, ".$outputFormat")
        $newFilePath = Join-Path -Path $outputDir -ChildPath $newFileName
        if (-not (Test-Path $newFilePath)) {
            rimage -f $outputFormat -q $outputQuality --quantization 100 --dithering 100 --width $newWidth -o $outputDir $file.FullName
            $processedFiles++
            Write-Host "Processed files: $processedFiles/$totalFiles --> $newFileName ($newWidth x $newHeight)"
        }
        else {
            Write-Host "File $newFileName already exists in the output directory. Skipping..."
        }
    }

    Write-Host "Processing completed."
    Write-Host ""
}
