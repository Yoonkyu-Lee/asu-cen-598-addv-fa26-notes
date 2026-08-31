# 강의 슬라이드 PPTX를 slides/*.pdf 로 변환한다.
#
# 두 가지를 반드시 지킨다.
#
# 1. Drive 미러 원본을 건드리지 않는다. 스크래치패드로 복사한 뒤 사본에서만 작업한다.
# 2. 숨김 슬라이드를 되살려서 변환한다. 그래야 PDF 쪽 번호 = 슬라이드에 인쇄된 번호가
#    되어 data-slide 앵커가 어긋날 자리가 없어진다. (자세한 이유는 CLAUDE.md 참조)
#
# ExportAsFixedFormat 의 PrintHiddenSlides 인자는 PowerShell 후기 바인딩에서
# msoTrue(-1) 를 못 받는다. 그래서 숨김을 먼저 풀고 SaveAs 를 쓴다.
#
# 사용법: powershell -File scripts/pptx2pdf.ps1

$ErrorActionPreference = 'Stop'

$src  = 'D:\Library\01 Immigration Documents\02 ASU\FA26\CEN 598  ADDV'
$out  = Join-Path $PSScriptRoot '..\slides' | Resolve-Path
$work = Join-Path $env:TEMP 'addv-pptx'

# PPTX 파일명 -> 노트와 stem 을 맞춘 PDF 파일명.
# 새 강의가 나오면 여기에 한 줄 추가한다. Schedule 표의 Lecture 번호를 따른다.
$map = [ordered]@{
  '01_Course Intro.pptx'                     = 'L01-course-intro.pdf'
  '02_Design and Verification Overview.pptx' = 'L02-design-and-verification-overview.pdf'
}

New-Item -ItemType Directory -Force $work | Out-Null
$pp = New-Object -ComObject PowerPoint.Application

foreach ($k in $map.Keys) {
  $from = Join-Path $src $k
  if (-not (Test-Path $from)) { Write-Warning "원본 없음, 건너뜀: $k"; continue }

  $copy = Join-Path $work $k
  Copy-Item $from $copy -Force

  $pres = $pp.Presentations.Open($copy, $false, $false, $false)
  $unhid = 0
  foreach ($s in $pres.Slides) {
    if ($s.SlideShowTransition.Hidden -ne 0) { $s.SlideShowTransition.Hidden = 0; $unhid++ }
  }
  $pres.SaveAs((Join-Path $out $map[$k]), 32)   # 32 = ppSaveAsPDF
  $total = $pres.Slides.Count
  $pres.Close()

  Write-Output "$($map[$k])  $total 장 (숨김 $unhid 장 되살림)"
}

$pp.Quit()
Write-Output ''
Write-Output 'PPTX 장수와 PDF 쪽 수가 같은지 확인:  node scripts/pagecount.mjs'
