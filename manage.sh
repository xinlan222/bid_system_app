#!/bin/bash
# Bid System 服务管理脚本

PROJECT_DIR="/root/.openclaw/workspace/bid_system_app"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 检查服务状态
check_status() {
    echo ""
    print_info "========== Bid System 服务状态 =========="
    echo ""

    # PostgreSQL
    if systemctl is-active --quiet postgresql; then
        echo -e "PostgreSQL:      ${GREEN}运行中${NC}"
    else
        echo -e "PostgreSQL:      ${RED}已停止${NC}"
    fi

    # FastAPI Backend
    if systemctl is-active --quiet bid-system-backend; then
        echo -e "FastAPI 后端:   ${GREEN}运行中${NC}"
    else
        echo -e "FastAPI 后端:   ${RED}已停止${NC}"
    fi

    echo ""
    print_info "========== 服务端口 =========="
    echo ""
    echo "PostgreSQL:     5432"
    echo "FastAPI 后端:   8000"
    echo "FastAPI 文档:   http://0.0.0.0:8000/docs"
    echo ""

    print_info "========== 日志查看 =========="
    echo ""
    echo "查看后端日志:  sudo journalctl -u bid-system-backend -f"
    echo "查看系统日志:  sudo journalctl -f"
    echo ""
}

# 启动所有服务
start_services() {
    print_info "启动 Bid System 服务..."

    systemctl start postgresql
    systemctl start bid-system-backend

    sleep 2
    check_status
}

# 停止所有服务
stop_services() {
    print_warning "停止 Bid System 服务..."

    systemctl stop bid-system-backend
    # PostgreSQL 可能被其他服务使用，默认不停止
    print_info "PostgreSQL 保持运行（可能被其他服务使用）"

    sleep 1
    check_status
}

# 重启所有服务
restart_services() {
    print_warning "重启 Bid System 服务..."

    systemctl restart postgresql
    systemctl restart bid-system-backend

    sleep 2
    check_status
}

# 查看后端日志
view_logs() {
    print_info "查看 FastAPI 后端日志（Ctrl+C 退出）..."
    echo ""
    journalctl -u bid-system-backend -f --no-pager
}

# 查看最近日志
view_recent_logs() {
    print_info "查看最近 50 条后端日志..."
    echo ""
    journalctl -u bid-system-backend -n 50 --no-pager
}

# 更新并重启
update_and_restart() {
    print_info "从 GitHub 拉取最新代码..."
    cd "$PROJECT_DIR"
    git pull origin main

    if [ $? -eq 0 ]; then
        print_success "代码更新成功"
        restart_services
    else
        print_error "代码更新失败，请检查"
    fi
}

# 查看服务健康状态
health_check() {
    echo ""
    print_info "========== 服务健康检查 =========="
    echo ""

    # 检查 PostgreSQL
    if PGPASSWORD=postgres psql -h localhost -U postgres -d bid_system_app -c "SELECT 1;" &>/dev/null; then
        echo -e "PostgreSQL:     ${GREEN}✓ 健康${NC}"
    else
        echo -e "PostgreSQL:     ${RED}✗ 异常${NC}"
    fi

    # 检查 FastAPI
    if curl -s http://localhost:8000/docs &>/dev/null; then
        echo -e "FastAPI:        ${GREEN}✓ 健康${NC}"
    else
        echo -e "FastAPI:        ${RED}✗ 异常${NC}"
    fi

    # 检查 Next.js 前端
    if curl -s http://localhost:3000/ &>/dev/null; then
        echo -e "Next.js 前端:   ${GREEN}✓ 健康${NC}"
    else
        echo -e "Next.js 前端:   ${RED}✗ 异常${NC}"
    fi

    echo ""
}

# 主菜单
show_menu() {
    echo ""
    echo "=========================================="
    echo "    Bid System 服务管理"
    echo "=========================================="
    echo "1. 查看服务状态"
    echo "2. 启动所有服务"
    echo "3. 停止所有服务"
    echo "4. 重启所有服务"
    echo "5. 查看实时日志"
    echo "6. 查看最近日志"
    echo "7. 拉取最新代码并重启"
    echo "8. 健康检查"
    echo "0. 退出"
    echo "=========================================="
    echo -n "请选择操作 [0-8]: "
}

# 主函数
main() {
    if [ $# -gt 0 ]; then
        # 命令行参数模式
        case "$1" in
            status) check_status ;;
            start) start_services ;;
            stop) stop_services ;;
            restart) restart_services ;;
            logs) view_logs ;;
            recent-logs) view_recent_logs ;;
            update) update_and_restart ;;
            health) health_check ;;
            *)
                echo "用法: $0 {status|start|stop|restart|logs|recent-logs|update|health}"
                exit 1
                ;;
        esac
    else
        # 交互模式
        while true; do
            show_menu
            read -r choice
            case $choice in
                1) check_status ;;
                2) start_services ;;
                3) stop_services ;;
                4) restart_services ;;
                5) view_logs ;;
                6) view_recent_logs ;;
                7) update_and_restart ;;
                8) health_check ;;
                0) print_info "退出"; exit 0 ;;
                *) print_error "无效选择，请重试" ;;
            esac
        done
    fi
}

# 运行主函数
main "$@"
