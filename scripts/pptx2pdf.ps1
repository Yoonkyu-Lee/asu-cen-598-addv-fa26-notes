# 강의 슬라이드 PPTX를 slides/*.pdf 로 변환한다.
#
# 세 가지를 반드시 지킨다.
#
# 1. lecture/ 의 원본을 건드리지 않는다. 스크래치패드로 복사한 뒤 사본에서만 작업한다.
# 2. 숨김 슬라이드를 되살려서 변환한다. 그래야 PDF 쪽 번호 = 슬라이드에 인쇄된 번호가
#    되어 data-slide 앵커가 어긋날 자리가 없어진다. (자세한 이유는 CLAUDE.md 참조)
# 3. 이미 slides/ 에 있는 PDF 는 건너뛴다. 다시 만들려면 -Force.
#
# LibreOffice 가 아니라 PowerPoint COM 을 쓴다. LibreOffice 는 텍스트 상자를 넘친 글자를
# 잘라버리고 수식(OMML)을 외곽선으로 내보내서, 변환본이 강사 화면과 달라진다.
#
# ExportAsFixedFormat 의 PrintHiddenSlides 인자는 PowerShell 후기 바인딩에서
# msoTrue(-1) 를 못 받는다. 그래서 숨김을 먼저 풀고 SaveAs 를 쓴다.
#
# 변환 뒤 쪽 수를 확인한다:  node scripts/pagecount.mjs
#
# 사용법: powershell -File scripts/pptx2pdf.ps1 [-Force]

param([switch]$Force)

$ErrorActionPreference = 'Stop'

$root = Resolve-Path (Join-Path $PSScriptRoot '..')
$src  = Join-Path $root 'lecture'
$out  = Join-Path $root 'slides'
$work = Join-Path $env:TEMP 'addv-pptx'

# PPTX 파일명 -> 노트와 stem 을 맞춘 PDF 파일명.
# 새 강의가 나오면 여기에 한 줄 추가한다.
#
# 앞의 번호는 강사가 자료에 붙인 것이고, 6번부터 강의 번호와 어긋난다.
# 강사가 Lab 1 릴리스를 06 으로 넣었기 때문이다. 강의 번호는 docs/schedule.md 가 단일 출처다.
# 05_FIFO_Design_Igor 는 강사가 처음부터 PDF 로 배포해서 여기 없다.
$map = [ordered]@{
  '01_Course Intro.pptx'                     = 'L01-course-intro.pdf'
  '02_Design and Verification Overview.pptx' = 'L02-design-and-verification-overview.pdf'
  '03_System Verilog for Design.pptx'        = 'L03-system-verilog-for-design.pdf'
  '04_Clock_Reset_Chetan.pptx'               = 'L04-clock-and-reset.pdf'
  '07_Pipelined CPU Design.pptx'             = 'L06-pipelined-cpu-design.pdf'
  '08_Efficient Design.pptx'                 = 'L07-efficient-design.pdf'
}

New-Item -ItemType Directory -Force $work | Out-Null

# 변환할 것만 추린다.
$todo = [ordered]@{}
foreach ($k in $map.Keys) {
  if (-not (Test-Path (Join-Path $src $k))) { Write-Warning "원본 없음, 건너뜀: $k"; continue }
  if ((Test-Path (Join-Path $out $map[$k])) -and -not $Force) {
    Write-Output "$($map[$k])  이미 있음, 건너뜀 (-Force 로 덮어쓴다)"
    continue
  }
  $todo[$k] = $map[$k]
}
if ($todo.Count -eq 0) { Write-Output ''; Write-Output '변환할 것이 없다.'; return }

$pp = New-Object -ComObject PowerPoint.Application

try {
  foreach ($k in $todo.Keys) {
    $copy = Join-Path $work $k
    Copy-Item (Join-Path $src $k) $copy -Force

    $pres = $pp.Presentations.Open($copy, $false, $false, $false)
    $unhid = 0
    foreach ($s in $pres.Slides) {
      if ($s.SlideShowTransition.Hidden -ne 0) { $s.SlideShowTransition.Hidden = 0; $unhid++ }
    }
    $total = $pres.Slides.Count
    $pres.SaveAs((Join-Path $out $todo[$k]), 32)   # 32 = ppSaveAsPDF
    $pres.Close()

    Write-Output "$($todo[$k])  $total 장 (숨김 $unhid 장 되살림)"
  }
}
finally { $pp.Quit() }

Write-Output ''
Write-Output 'PPTX 장수와 PDF 쪽 수가 같은지 확인:  node scripts/pagecount.mjs'
