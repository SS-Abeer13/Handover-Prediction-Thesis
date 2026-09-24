@echo off
REM Full development pipeline (everything except the locked external route).
setlocal
cd /d "%~dp0"
if not defined HO_EPOCHS set HO_EPOCHS=25
set PYTHONPATH=%~dp0src

echo === R7-R10  prepare
python -m hoproj.pipeline.stage01_prepare                      || goto :err
echo === R11-R13 experiments
python -m hoproj.pipeline.stage02_experiment --experiment main              || goto :err
python -m hoproj.pipeline.stage02_experiment --experiment leakage_study     || goto :err
python -m hoproj.pipeline.stage02_experiment --experiment ablation_features || goto :err
python -m hoproj.pipeline.stage02_experiment --experiment multitask         || goto :err
echo === R14 uncertainty
python -m hoproj.pipeline.stage03_uncertainty --model gru      || goto :err
echo === R16 report
python -m hoproj.pipeline.stage05_report                       || goto :err

echo.
echo Done. Reports are in reports\, artefacts in artifacts\.
echo The external route is still locked. To open it:
echo    python -m hoproj.pipeline.stage04_external --freeze --model gru
echo    python -m hoproj.pipeline.stage04_external --model gru
goto :eof

:err
echo.
echo FAILED at the step above.
exit /b 1
