@echo off
chcp 65001 > nul
title UTN Parana - Suite de Simulacion Electroneumatica y SCADA Mecatronico
echo ===========================================================================
echo  UTN FACULTAD REGIONAL PARANA - TECNICATURA SUPERIOR EN MECATRONICA
echo  Catedra: Mecatronica II - Alumno: Hugo Ariel Martinez
echo  Iniciando Simulador Electroneumatico y SCADA Clasificador ISA-101...
echo ===========================================================================

where node >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    cd /d "%~dp0Simulador_SCADA"
    node server.js --open
) else (
    echo [INFO] Abriendo simulador directamente en el navegador...
    start "" "%~dp0Simulador_SCADA\index.html"
)
