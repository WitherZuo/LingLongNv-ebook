$sources_folder = ".\src\"
$chapters = (Get-ChildItem .\src\*.md | Sort-Object Name | ForEach-Object { $sources_folder+$_.Name })

foreach ($chapter in $chapters) {
    Get-Content $chapter | Out-File -Append .\fonts\full.txt 
}

fonttools subset .\fonts\JingHuaLaoSongTi_v3.ttf --text-file=.\fonts\full.txt --output-file=.\fonts\JingHuaLaoSongTi.ttf
fonttools subset .\fonts\simhei.ttf --text-file=.\fonts\title.txt --output-file=.\fonts\simhei-subset.ttf

fonttools ttLib.woff2 compress ".\fonts\JingHuaLaoSongTi.ttf" -o ".\fonts\JingHuaLaoSongTi.woff2"
fonttools ttLib.woff2 compress ".\fonts\simhei-subset.ttf" -o ".\fonts\SimHei.woff2"    

if (-not (Test-Path .\out)) {
    New-Item -Type Directory out
}

pandoc -o .\out\linglongnv.epub .\book.yaml `
    --css=.\styles\book.css `
    --epub-embed-font=.\fonts\JingHuaLaoSongTi.woff2 `
    --epub-embed-font=.\fonts\SimHei.woff2 `
    $chapters

Remove-Item .\fonts\full.txt
Remove-Item .\fonts\JingHuaLaoSongTi.ttf
Remove-Item .\fonts\simhei-subset.ttf
Remove-Item .\fonts\*.woff2