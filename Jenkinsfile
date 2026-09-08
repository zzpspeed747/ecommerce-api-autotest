pipeline {
    agent any

    options {
        // 不使用Jenkins默认隐式拉取，后面手动checkout
        skipDefaultCheckout(true)

       

        // 防止两次构建同时占用8888端口
        disableConcurrentBuilds()

        buildDiscarder(
            logRotator(
                numToKeepStr: '10',
                artifactNumToKeepStr: '5'
            )
        )
    }

    environment {
        PYTHONIOENCODING = 'utf-8'
        PYTHONUTF8 = '1'

        TEST_ENV = 'jenkins'

        BASE_URL = 'http://127.0.0.1:8888/api/private/v1'

        // Jenkins使用YAML；你本地仍可使用Excel
        CASE_FILE = './data/test_cases_100.yaml'

        HTTP_CONNECT_TIMEOUT = '3.05'
        HTTP_READ_TIMEOUT = '10'

        DB_ENABLED = 'false'
    }

    stages {
        stage('拉取测试项目') {
            steps {
                // 清理上一次构建残留
                deleteDir()

                // 拉取当前Pipeline配置的测试项目仓库
                checkout scm
            }
        }

        stage('拉取Mock项目') {
            steps {
                dir('_mock') {
                    git(
                        branch: 'main',
                        
                        url: 'https://github.com/zzpspeed747/ecommerce-mock-server.git'
                    )
                }
            }
        }

        stage('检查项目结构') {
            steps {
                bat '''
                    chcp 65001

                    echo 当前Jenkins工作目录：
                    cd

                    if not exist "requirements.txt" (
                        echo 未找到测试项目requirements.txt
                        exit /b 1
                    )

                    if not exist "_mock\\mock_server.py" (
                        echo 未找到_mock\\mock_server.py
                        exit /b 1
                    )

                    if not exist "data\\test_cases_100.yaml" (
                        echo 未找到100条YAML测试用例
                        exit /b 1
                    )

                    echo 项目结构检查通过
                '''
            }
        }

        stage('创建Python环境') {
            steps {
                bat '''
                    chcp 65001

                    python --version
                    git --version

                    if not exist ".venv" (
                        python -m venv .venv
                    )

                    .venv\\Scripts\\python.exe -m pip install --upgrade pip

                    .venv\\Scripts\\python.exe -m pip install ^
                        -r requirements.txt

                    if exist "_mock\\requirements_mock.txt" (
                        .venv\\Scripts\\python.exe -m pip install ^
                            -r _mock\\requirements_mock.txt
                    ) else (
                        .venv\\Scripts\\python.exe -m pip install Flask
                    )
                '''
            }
        }

        stage('准备报告目录') {
            steps {
                bat '''
                    chcp 65001

                    if not exist "report" mkdir report
                    if not exist "log" mkdir log
                '''
            }
        }

        stage('执行框架单元测试') {
            steps {
                bat '''
                    chcp 65001

                    .venv\\Scripts\\python.exe -m pytest tests ^
                        -v ^
                        --junitxml=report\\junit-unit.xml
                '''
            }
        }

    stage('API Integration Tests') {
    steps {
        powershell '''
            $ErrorActionPreference = "Stop"

            $pythonPath = Join-Path `
                $env:WORKSPACE `
                ".venv\\Scripts\\python.exe"

            $mockDirectory = Join-Path `
                $env:WORKSPACE `
                "_mock"

            $mockScript = Join-Path `
                $mockDirectory `
                "mock_server.py"

            $mockLog = Join-Path `
                $env:WORKSPACE `
                "report\\mock-server.log"

            $mockErrorLog = Join-Path `
                $env:WORKSPACE `
                "report\\mock-server-error.log"

            $healthUrl = `
                "http://127.0.0.1:8888/api/private/v1/health"

            $mockProcess = $null

            try {
                Write-Host "Starting Mock server..."

                $mockProcess = Start-Process `
                    -FilePath $pythonPath `
                    -ArgumentList "`"$mockScript`"" `
                    -WorkingDirectory $mockDirectory `
                    -RedirectStandardOutput $mockLog `
                    -RedirectStandardError $mockErrorLog `
                    -PassThru

                Write-Host "Mock PID: $($mockProcess.Id)"

                $healthy = $false

                for ($attempt = 1; $attempt -le 10; $attempt++) {
                    Start-Sleep -Seconds 1

                    $runningProcess = Get-Process `
                        -Id $mockProcess.Id `
                        -ErrorAction SilentlyContinue

                    if (-not $runningProcess) {
                        Write-Host "Mock process exited unexpectedly"

                        if (Test-Path $mockErrorLog) {
                            Get-Content $mockErrorLog
                        }

                        throw "Mock process exited unexpectedly"
                    }

                    try {
                        $response = Invoke-RestMethod `
                            -Uri $healthUrl `
                            -Method Get `
                            -TimeoutSec 2

                        if ($response.data.status -eq "UP") {
                            Write-Host "Mock health check passed"
                            $healthy = $true
                            break
                        }
                    }
                    catch {
                        Write-Host "Waiting for Mock: $attempt/10"
                    }
                }

                if (-not $healthy) {
                    if (Test-Path $mockErrorLog) {
                        Get-Content $mockErrorLog
                    }

                    throw "Mock health check failed"
                }

                Write-Host "Collecting API test cases..."

                & $pythonPath `
                    -m pytest `
                    "testcases\\test_runner.py" `
                    --collect-only `
                    -q

                if ($LASTEXITCODE -ne 0) {
                    throw "Test case collection failed"
                }

                Write-Host "Running API test cases..."

                & $pythonPath `
                    -m pytest `
                    "testcases\\test_runner.py" `
                    -v `
                    "--junitxml=report\\junit-api.xml" `
                    "--alluredir=report\\json_report" `
                    --clean-alluredir

                $pytestExitCode = $LASTEXITCODE

                if ($pytestExitCode -ne 0) {
                    throw "API tests failed, pytest exit code: $pytestExitCode"
                }

                Write-Host "API tests passed"
            }
            finally {
                if ($mockProcess) {
                    $runningProcess = Get-Process `
                        -Id $mockProcess.Id `
                        -ErrorAction SilentlyContinue

                    if ($runningProcess) {
                        Write-Host "Stopping Mock server..."

                        Stop-Process `
                            -Id $mockProcess.Id `
                            -Force

                        Wait-Process `
                            -Id $mockProcess.Id `
                            -ErrorAction SilentlyContinue

                        Write-Host "Mock server stopped"
                    }
                }
            }
        '''
    }
}

post {
    always {
        junit(
            testResults: 'report/junit-*.xml',
            allowEmptyResults: true
        )

        script {
            if (fileExists('report/json_report')) {
                allure(
                    includeProperties: false,
                    jdk: '',
                    results: [
                        [path: 'report/json_report']
                    ]
                )
            } else {
                echo 'No Allure results were generated'
            }
        }

        archiveArtifacts(
            artifacts: 'report/**/*, log/**/*',
            allowEmptyArchive: true,
            fingerprint: true
        )
    }

    success {
        echo 'Unit tests and API tests passed'
    }

    failure {
        echo 'Pipeline failed, check JUnit, Allure and Mock logs'
    }
}
}