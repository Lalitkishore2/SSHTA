$ErrorActionPreference = "Stop"
try {
    $docxPath = "C:\Users\LALITKO\Desktop\projects\research paper\SSHTA_IEEE_Paper.docx"
    $pdfPath1 = "C:\Users\LALITKO\Desktop\projects\research paper\SSHTA_IEEE_Paper.pdf"
    $pdfPath2 = "C:\Users\LALITKO\Desktop\projects\research paper\SSHTA _ A Three Tier Hybrid Memory Architecture for Low Power High Bandwidth Super APU Design - main.pdf"
    
    Write-Host "Starting Word COM application..."
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    
    Write-Host "Opening document: $docxPath"
    $doc = $word.Documents.Open($docxPath, $false, $true) # Open read-only
    
    Write-Host "Exporting to $pdfPath1..."
    $doc.SaveAs([ref] $pdfPath1, [ref] 17) # 17 is wdFormatPDF
    
    Write-Host "Exporting to $pdfPath2..."
    $doc.SaveAs([ref] $pdfPath2, [ref] 17)
    $doc.Close($false)

    $docxX = "C:\Users\LALITKO\Desktop\projects\research paper\SSHTA_X_IEEE_Paper.docx"
    $pdfX  = "C:\Users\LALITKO\Desktop\projects\research paper\SSHTA_X_IEEE_Paper.pdf"
    if (Test-Path $docxX) {
        Write-Host "Opening document: $docxX"
        $docX = $word.Documents.Open($docxX, $false, $true)
        Write-Host "Exporting to $pdfX..."
        $docX.SaveAs([ref] $pdfX, [ref] 17)
        $docX.Close($false)
    }
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
    Write-Host "PDF Export COMPLETE AND VERIFIED!"
} catch {
    Write-Host "PDF Export failed: $($_.Exception.Message)"
}
