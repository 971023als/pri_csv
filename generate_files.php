<?php
require 'vendor/autoload.php';
use PhpOffice\PhpSpreadsheet\Spreadsheet;
use PhpOffice\PhpSpreadsheet\Writer\Xlsx;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // 입력 데이터 가져오기
    $legalBasis = htmlspecialchars($_POST['legalBasis']);
    $collectionPurpose = htmlspecialchars($_POST['collectionPurpose']);
    $collectionData = htmlspecialchars($_POST['collectionData']);
    $retentionPeriod = htmlspecialchars($_POST['retentionPeriod']);
    $usagePurpose = htmlspecialchars($_POST['usagePurpose']);
    $thirdParty = htmlspecialchars($_POST['thirdParty']);
    $provisionPurpose = htmlspecialchars($_POST['provisionPurpose']);
    $destructionMethod = htmlspecialchars($_POST['destructionMethod']);

    // HTML 파일 생성
    $policy = "
    <h1>개인정보 처리방침</h1>
    <h2>1. 개인정보 수집</h2>
    <p>법적근거: {$legalBasis}</p>
    <p>수집 목적: {$collectionPurpose}</p>
    <p>수집 항목: {$collectionData}</p>
    <p>보유 기간: {$retentionPeriod}</p>
    <h2>2. 개인정보 이용</h2>
    <p>이용 목적: {$usagePurpose}</p>
    <h2>3. 개인정보 제공</h2>
    <p>제공 대상: {$thirdParty}</p>
    <p>제공 목적: {$provisionPurpose}</p>
    <h2>4. 개인정보 파기</h2>
    <p>파기 방법: {$destructionMethod}</p>
    ";
    $htmlFile = 'privacy_policy.html';
    file_put_contents($htmlFile, $policy);

    // 엑셀 파일 생성
    $spreadsheet = new Spreadsheet();
    $sheet = $spreadsheet->getActiveSheet();
    $sheet->setTitle('개인정보 흐름표');
    $sheet->setCellValue('A1', '단계');
    $sheet->setCellValue('B1', '내용');
    $sheet->setCellValue('A2', '수집');
    $sheet->setCellValue('B2', "법적근거: {$legalBasis}\n수집목적: {$collectionPurpose}\n수집항목: {$collectionData}\n보유기간: {$retentionPeriod}");
    $sheet->setCellValue('A3', '이용');
    $sheet->setCellValue('B3', $usagePurpose);
    $sheet->setCellValue('A4', '제공');
    $sheet->setCellValue('B4', "{$thirdParty}: {$provisionPurpose}");
    $sheet->setCellValue('A5', '파기');
    $sheet->setCellValue('B5', $destructionMethod);
    $excelFile = 'privacy_flowchart.xlsx';
    $writer = new Xlsx($spreadsheet);
    $writer->save($excelFile);

    echo "<a href='{$htmlFile}' download>HTML 다운로드</a><br>";
    echo "<a href='{$excelFile}' download>엑셀 다운로드</a><br>";
}
?>
