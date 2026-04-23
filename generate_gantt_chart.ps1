$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Drawing

$tasks = @(
    @{ Name = "Initial Planning and Legal Chatbot Concept Development"; Start = [datetime]"2025-09-25"; End = [datetime]"2025-10-31" },
    @{ Name = "Initial System Development"; Start = [datetime]"2025-11-01"; End = [datetime]"2025-11-26" },
    @{ Name = "Project Direction Change (Supervisor Feedback Milestone)"; Start = [datetime]"2025-11-27"; End = [datetime]"2025-12-10" },
    @{ Name = "Research and Scope Refinement Phase"; Start = [datetime]"2025-12-11"; End = [datetime]"2026-02-25" },
    @{ Name = "Dataset Transition (Westminster Regulations)"; Start = [datetime]"2026-02-26"; End = [datetime]"2026-03-02" },
    @{ Name = "Data Preprocessing and Embedding Regeneration"; Start = [datetime]"2026-03-03"; End = [datetime]"2026-03-15" },
    @{ Name = "RAG System Integration and Refinement"; Start = [datetime]"2026-03-16"; End = [datetime]"2026-03-28" },
    @{ Name = "Experimental Design and Setup"; Start = [datetime]"2026-03-29"; End = [datetime]"2026-04-05" },
    @{ Name = "Experiment Execution"; Start = [datetime]"2026-04-06"; End = [datetime]"2026-04-08" },
    @{ Name = "Manual Evaluation"; Start = [datetime]"2026-04-09"; End = [datetime]"2026-04-18" },
    @{ Name = "Results Analysis and Visualisation"; Start = [datetime]"2026-04-19"; End = [datetime]"2026-04-21" },
    @{ Name = "Report Drafting (Initial Writing)"; Start = [datetime]"2026-03-20"; End = [datetime]"2026-04-10" },
    @{ Name = "Final Report Writing and Submission"; Start = [datetime]"2026-04-22"; End = [datetime]"2026-04-23" }
)

$palette = @(
    "#4E79A7",
    "#F28E2B",
    "#E15759",
    "#76B7B2",
    "#59A14F",
    "#EDC948",
    "#B07AA1",
    "#FF9DA7"
)

function New-BrushFromHex {
    param([string]$Hex)
    return New-Object System.Drawing.SolidBrush ([System.Drawing.ColorTranslator]::FromHtml($Hex))
}

$width = 4800
$height = 3000
$leftMargin = 1500
$rightMargin = 180
$topMargin = 220
$bottomMargin = 360
$plotWidth = $width - $leftMargin - $rightMargin
$plotHeight = $height - $topMargin - $bottomMargin
$rowHeight = [double]$plotHeight / $tasks.Count
$barHeight = [double]($rowHeight * 0.52)

$minDate = ($tasks | ForEach-Object Start | Measure-Object -Minimum).Minimum
$maxTaskEnd = ($tasks | ForEach-Object End | Measure-Object -Maximum).Maximum
$axisStart = Get-Date -Year $minDate.Year -Month $minDate.Month -Day 1
$axisEnd = (Get-Date -Year $maxTaskEnd.Year -Month $maxTaskEnd.Month -Day 1).AddMonths(1)
$totalDays = ($axisEnd - $axisStart).Days

$bitmap = New-Object System.Drawing.Bitmap $width, $height
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
$graphics.Clear([System.Drawing.Color]::White)

$titleFont = New-Object System.Drawing.Font("Times New Roman", 52, [System.Drawing.FontStyle]::Bold)
$labelFont = New-Object System.Drawing.Font("Times New Roman", 30, [System.Drawing.FontStyle]::Regular)
$tickFont = New-Object System.Drawing.Font("Arial", 22, [System.Drawing.FontStyle]::Regular)
$taskFont = New-Object System.Drawing.Font("Arial", 24, [System.Drawing.FontStyle]::Regular)

$textBrush = [System.Drawing.Brushes]::Black
$axisPen = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(120, 120, 120)), 3
$gridPen = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(218, 223, 230)), 2
$gridPen.DashStyle = [System.Drawing.Drawing2D.DashStyle]::Dash

$titleRect = New-Object System.Drawing.RectangleF 0, 45, $width, 90
$titleFormat = New-Object System.Drawing.StringFormat
$titleFormat.Alignment = [System.Drawing.StringAlignment]::Center
$graphics.DrawString("Project Gantt Chart", $titleFont, $textBrush, $titleRect, $titleFormat)

$plotTop = $topMargin
$plotBottom = $topMargin + $plotHeight
$plotLeft = $leftMargin
$plotRight = $leftMargin + $plotWidth

$month = Get-Date $axisStart
while ($month -le $axisEnd) {
    $offsetDays = ($month - $axisStart).Days
    $x = [single]($plotLeft + ($offsetDays / $totalDays) * $plotWidth)
    $graphics.DrawLine($gridPen, $x, $plotTop, $x, $plotBottom)

    if ($month -lt $axisEnd) {
        $state = $graphics.Save()
        $graphics.TranslateTransform($x + 10, $plotBottom + 120)
        $graphics.RotateTransform(35)
        $graphics.DrawString($month.ToString("yyyy-MM-dd"), $tickFont, $textBrush, 0, 0)
        $graphics.Restore($state)
    }

    $month = $month.AddMonths(1)
}

for ($i = 0; $i -lt $tasks.Count; $i++) {
    $task = $tasks[$i]
    $centerY = [double]($plotTop + ($i + 0.5) * $rowHeight)
    $barY = [single]($centerY - ($barHeight / 2))
    $taskTop = [single]($plotTop + $i * $rowHeight)

    $taskOffset = ($task.Start - $axisStart).Days
    $taskDuration = (($task.End - $task.Start).Days + 1)
    $barX = [single]($plotLeft + ($taskOffset / $totalDays) * $plotWidth)
    $barWidth = [single](($taskDuration / $totalDays) * $plotWidth)

    $labelRect = New-Object System.Drawing.RectangleF 30, ($centerY - 34), ($leftMargin - 60), 68
    $labelFormat = New-Object System.Drawing.StringFormat
    $labelFormat.Alignment = [System.Drawing.StringAlignment]::Far
    $labelFormat.LineAlignment = [System.Drawing.StringAlignment]::Center
    $graphics.DrawString($task.Name, $taskFont, $textBrush, $labelRect, $labelFormat)

    $brush = New-BrushFromHex $palette[$i % $palette.Count]
    $graphics.FillRectangle($brush, $barX, $barY, $barWidth, [single]$barHeight)
    $graphics.DrawRectangle($axisPen, $barX, $barY, $barWidth, [single]$barHeight)
    $brush.Dispose()

    if ($i -lt ($tasks.Count - 1)) {
        $graphics.DrawLine($gridPen, $plotLeft, ($taskTop + $rowHeight), $plotRight, ($taskTop + $rowHeight))
    }
}

$graphics.DrawLine($axisPen, $plotLeft, $plotBottom, $plotRight, $plotBottom)
$graphics.DrawLine($axisPen, $plotLeft, $plotTop, $plotLeft, $plotBottom)

$xLabelRect = New-Object System.Drawing.RectangleF $plotLeft, ($height - 130), $plotWidth, 50
$xLabelFormat = New-Object System.Drawing.StringFormat
$xLabelFormat.Alignment = [System.Drawing.StringAlignment]::Center
$graphics.DrawString("Project Timeline", $labelFont, $textBrush, $xLabelRect, $xLabelFormat)

$pngOutputPath = Join-Path $PSScriptRoot "gantt_chart.png"
$bitmap.SetResolution(300, 300)
$bitmap.Save($pngOutputPath, [System.Drawing.Imaging.ImageFormat]::Png)

$titleFont.Dispose()
$labelFont.Dispose()
$tickFont.Dispose()
$taskFont.Dispose()
$axisPen.Dispose()
$gridPen.Dispose()
$graphics.Dispose()
$bitmap.Dispose()

Write-Output "Saved $pngOutputPath"
