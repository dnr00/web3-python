import asyncio
import psutil
import datetime
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
import subprocess
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = 'TG_API_TOKEN'
GROUP_CHAT_ID = 'GROUP_CHAT_ID'

# 스크립트 경로 설정
BASE_DIR = "/home/dnr2901/bot"
CONTROL_DIR = os.path.join(BASE_DIR, "control")
BATCH_DIR = os.path.join(BASE_DIR, "batch")
BATCH2_DIR = os.path.join(BASE_DIR, "batch2")
JNKY_DIR = os.path.join(BASE_DIR, "jnky")

async def get_python3_processes():
    python3_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'create_time', 'cmdline']):
        try:
            if 'python3' in proc.info['name']:
                pid = proc.info['pid']
                name = proc.info['name']
                create_time = proc.info['create_time']
                cmdline = proc.info['cmdline']
                
                script_name = "Unknown"
                if cmdline and len(cmdline) > 1:
                    script_path = cmdline[1]
                    script_name = os.path.basename(script_path)
                
                python3_processes.append((pid, name, create_time, script_name))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return python3_processes

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    processes = await get_python3_processes()
    if processes:
        message = "실행 중인 Python3 프로세스:\n"
        for pid, name, create_time, script_name in processes:
            uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(create_time)
            uptime_str = str(uptime).split('.')[0]  # 밀리초 제거
            message += f"PID: {pid}, 이름: {name}, 스크립트: {script_name}, 가동 시간: {uptime_str}\n"
    else:
        message = "실행 중인 Python3 프로세스가 없습니다."
    await update.message.reply_text(message)

async def kill_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("종료할 프로세스의 PID를 입력하세요.")
        return
    try:
        pid = int(context.args[0])
        psutil.Process(pid).terminate()
        await update.message.reply_text(f"PID {pid}인 프로세스를 종료했습니다.")
    except psutil.NoSuchProcess:
        await update.message.reply_text(f"PID {pid}인 프로세스를 찾을 수 없습니다.")
    except ValueError:
        await update.message.reply_text("올바른 PID를 입력하세요.")

async def restart_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("재시작할 프로세스의 PID와 명령어를 입력하세요.")
        return
    try:
        pid = int(context.args[0])
        command = ' '.join(context.args[1:])
        psutil.Process(pid).terminate()
        await asyncio.create_subprocess_shell(f"nohup {command} &")
        await update.message.reply_text(f"PID {pid}인 프로세스를 종료하고 '{command}'로 재시작했습니다.")
    except psutil.NoSuchProcess:
        await update.message.reply_text(f"PID {pid}인 프로세스를 찾을 수 없습니다.")
    except ValueError:
        await update.message.reply_text("올바른 PID를 입력하세요.")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1. main_process_vm.py", callback_data='1')],
        [InlineKeyboardButton("2. main_process_vm2.py", callback_data='2')],
        [InlineKeyboardButton("3. main_process_vm3.py", callback_data='3')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('어느 파일을 실행하시겠습니까?', reply_markup=reply_markup)

def run_script(script_path):
    try:
        process = subprocess.Popen(['python3', script_path], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   cwd=os.path.dirname(script_path))
        return process
    except Exception as e:
        return str(e)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    script_path = ""
    if query.data == '1':
        script_path = os.path.join(BATCH_DIR, "main_process_vm.py")
    elif query.data == '2':
        script_path = os.path.join(BATCH2_DIR, "main_process_vm2.py")
    elif query.data == '3':
        script_path = os.path.join(JNKY_DIR, "main_process_vm3.py")

    if script_path:
        process = run_script(script_path)
        if isinstance(process, subprocess.Popen):
            await query.edit_message_text(f"스크립트 '{os.path.basename(script_path)}'을 백그라운드에서 실행했습니다.")
        else:
            await query.edit_message_text(f"스크립트 실행 중 오류가 발생했습니다: {process}")
    else:
        await query.edit_message_text("잘못된 선택입니다.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
사용 가능한 명령어:

/help - 이 도움말 메시지를 표시합니다.
/status - 현재 실행 중인 Python3 프로세스의 상태를 표시합니다.
/kill <PID> - 지정된 PID의 프로세스를 종료합니다.
/restart <PID> <명령어> - 지정된 PID의 프로세스를 종료하고 주어진 명령어로 재시작합니다.
/start - 실행할 스크립트를 선택하고 백그라운드에서 실행합니다.

자동 기능:
- 'batch' 또는 'faucet_interaction'이 포함된 파일명의 프로세스가 2분 이상 실행된 경우 자동으로 재시작됩니다.
"""
    await update.message.reply_text(help_text)
async def check_and_restart_processes(context: ContextTypes.DEFAULT_TYPE):
    processes = await get_python3_processes()
    now = datetime.datetime.now()
    for pid, name, create_time, script_name in processes:
        uptime = now - datetime.datetime.fromtimestamp(create_time)
        if uptime > datetime.timedelta(minutes=2) and ('batch' in script_name or 'faucet_interaction' in script_name or 'mnemonic' in script_name):
            command = f"python3 {script_name}"
            try:
                psutil.Process(pid).terminate()
                await asyncio.create_subprocess_shell(f"nohup {command} &")
                message = f"자동 재시작: PID {pid}인 프로세스 '{script_name}'을(를) 재시작했습니다."
                await context.bot.send_message(chat_id=context.job.chat_id, text=message)
            except Exception as e:
                error_message = f"자동 재시작 실패: PID {pid}, 스크립트 '{script_name}' - 오류: {str(e)}"
                await context.bot.send_message(chat_id=context.job.chat_id, text=error_message)

def main():
    application = Application.builder().token(API_TOKEN).build()
    
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("kill", kill_process))
    application.add_handler(CommandHandler("restart", restart_process))
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    
    # 주기적으로 프로세스 확인 및 재시작
    job_queue = application.job_queue
    job_queue.run_repeating(check_and_restart_processes, interval=30, first=10, chat_id=GROUP_CHAT_ID)
    
    application.run_polling()

if __name__ == '__main__':
    main()