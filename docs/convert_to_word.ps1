$ErrorActionPreference = "Stop"

$docsDir = "C:\absensi eskul pencak silat\docs"
$umlDir = "$docsDir\UML"

$imgMap = @{
    "[[IMG_USE_CASE]]"   = "$umlDir\use case diagram sistem absensi ekstrakurikuler pencak silat.png"
    "[[IMG_ACT_ADMIN]]"   = "$umlDir\activity diagram admin.png"
    "[[IMG_ACT_PELATIH]]" = "$umlDir\activity diagram pelatih.png"
    "[[IMG_ACT_ANGGOTA]]" = "$umlDir\activity diagram anggota.png"
}

$docs = @(
    @{ Html = "$docsDir\SRS_SilatTrack.html"; Docx = "$docsDir\SRS_SilatTrack.docx"; Name = "SRS (Software Requirements Specification)" },
    @{ Html = "$docsDir\PRD_SilatTrack.html"; Docx = "$docsDir\PRD_SilatTrack.docx"; Name = "PRD (Product Requirements Document)" },
    @{ Html = "$docsDir\ERD_SilatTrack.html"; Docx = "$docsDir\ERD_SilatTrack.docx"; Name = "ERD & Data Dictionary" },
    @{ Html = "$docsDir\MANUAL_BOOK_SilatTrack.html"; Docx = "$docsDir\MANUAL_BOOK_SilatTrack.docx"; Name = "Manual Book (Buku Panduan Pengguna)" }
)

Write-Host "Menginisialisasi Microsoft Word COM Automation..." -ForegroundColor Cyan
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0 # wdAlertsNone

try {
    foreach ($item in $docs) {
        $htmlPath = $item.Html
        $docxPath = $item.Docx
        $docName = $item.Name

        Write-Host "`n========================================================" -ForegroundColor Magenta
        Write-Host "Memproses: $docName" -ForegroundColor Yellow
        Write-Host "========================================================" -ForegroundColor Magenta

        if (-not (Test-Path $htmlPath)) {
            Write-Warning "File HTML tidak ditemukan: $htmlPath"
            continue
        }

        # 1. Buka HTML & simpan ke format dasar DOCX
        Write-Host "  [1/4] Mengonversi HTML ke struktur Word..."
        $doc = $word.Documents.Open($htmlPath, $false, $false)

        # Atur ukuran A4 dan margin
        try {
            $doc.PageSetup.PaperSize = 7 # wdPaperA4
            $doc.PageSetup.TopMargin = 54 # 0.75 in
            $doc.PageSetup.BottomMargin = 54
            $doc.PageSetup.LeftMargin = 54
            $doc.PageSetup.RightMargin = 54
        } catch {}

        # AutoFit seluruh tabel
        $tblCount = $doc.Tables.Count
        Write-Host "  [2/4] Merapikan $tblCount tabel ke lebar halaman..."
        foreach ($tbl in $doc.Tables) {
            try {
                $tbl.AutoFitBehavior(2) # wdAutoFitWindow
            } catch {}
        }

        if (Test-Path $docxPath) {
            Remove-Item $docxPath -Force
        }
        $doc.SaveAs2($docxPath, 16) # wdFormatXMLDocument = 16
        $doc.Close(0)

        # 2. Buka berkas DOCX native untuk penyematan gambar & header/footer
        Write-Host "  [3/4] Menyematkan diagram gambar beresolusi tinggi..."
        $doc = $word.Documents.Open($docxPath, $false, $false)

        # Ganti placeholder dengan gambar nyata
        foreach ($ph in $imgMap.Keys) {
            $imgPath = $imgMap[$ph]
            if (-not (Test-Path $imgPath)) { continue }

            $find = $doc.Content.Find
            $find.ClearFormatting()
            $find.Text = $ph
            if ($find.Execute()) {
                $rng = $find.Parent
                $rng.Text = ""
                $shape = $rng.InlineShapes.AddPicture($imgPath, $false, $true)
                if ($shape.Width -gt 460) {
                    $ratio = 460.0 / $shape.Width
                    $shape.Width = 460
                    $shape.Height = [int]($shape.Height * $ratio)
                }
                Write-Host "    -> Berhasil menyematkan: $(Split-Path $imgPath -Leaf)" -ForegroundColor Green
            }
        }

        # Konfigurasi Header & Footer halaman 2+
        Write-Host "  [4/4] Mengonfigurasi header & footer resmi..."
        foreach ($sec in $doc.Sections) {
            $sec.PageSetup.DifferentFirstPageHeaderFooter = $true

            # Header
            $hdr = $sec.Headers.Item(1)
            $hdr.Range.Text = "SilatTrack: Sistem Absensi & Manajemen Eskul Pencak Silat"
            $hdr.Range.ParagraphFormat.Alignment = 2 # Right
            $hdr.Range.Font.Name = "Calibri"
            $hdr.Range.Font.Size = 8.5
            $hdr.Range.Font.Color = 0x666666

            # Footer
            $ftr = $sec.Footers.Item(1)
            $ftr.Range.Text = "Dokumen Resmi SilatTrack v1.3 | "
            $ftr.Range.Font.Name = "Calibri"
            $ftr.Range.Font.Size = 8.5
            $ftr.Range.Font.Color = 0x666666
            $rngFtr = $ftr.Range
            $rngFtr.Collapse(0) # Collapse to end
            $doc.Fields.Add($rngFtr, 33) | Out-Null # wdFieldPage = 33
        }

        $doc.Save()
        $doc.Close(0)

        $fileSize = (Get-Item $docxPath).Length
        $sizeKB = [math]::Round($fileSize / 1024, 1)
        Write-Host "  [SELESAI] $docName tersimpan rapi ($sizeKB KB)!" -ForegroundColor Green
    }
} finally {
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}

Write-Host "`nSeluruh 4 dokumen Word (.docx) berhasil dibuat dengan sempurna!" -ForegroundColor Green
