#!/usr/bin/env python3
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# Logging setup
logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO)
log = logging.getLogger("alcoach")

BOT_TOKEN = os.getenv("BOT_TOKEN")

# In-memory storage (Local database for bot)
BOT_DATA = {
    "study": [],     # {"subject": "Physics", "hours": 3}
    "habits": [],    # {"habit": "Wake up 5.30", "done": True}
    "tasks": [],     # {"text": "Do past paper", "done": False}
    "mistakes": []   # {"topic": "Mechanics", "wrong": "...", "correct": "..."}
}

# Subiects & Options
SUBJ = {"Physics": "Physics", "Pure": "Pure Math", "Applied": "Applied Math", "Chemistry": "Chemistry"}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🔥 **A/L 2026 AI Coach Bot** 🔥\n\n"
        "ඔබගේ දෛනික අධ්‍යයන කටයුතු පහත විධාන හරහා පාලනය කරන්න:"
    )
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 Study Hours", callback_data="menu_study"), InlineKeyboardButton("✅ Habits", callback_data="menu_habits")],
        [InlineKeyboardButton("📅 Tasks & Planner", callback_data="menu_tasks"), InlineKeyboardButton("🧠 Mistakes", callback_data="menu_mistakes")]
    ])
    if update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode="Markdown", reply_markup=markup)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_study":
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Log Study Hours", callback_data="st_log"), InlineKeyboardButton("📊 View Log", callback_data="st_view")],
            [InlineKeyboardButton("⬅️ Main Menu", callback_data="main_menu")]
        ])
        await query.message.edit_text("📚 **Study Hours Management**", parse_mode="Markdown", reply_markup=markup)
    
    elif data == "st_log":
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(v, callback_data=f"st_sub_{k}")] for k, v in SUBJ.items()
        ] + [[InlineKeyboardButton("⬅️ Back", callback_data="menu_study")]])
        await query.message.edit_text("විෂය තෝරන්න:", parse_mode="Markdown", reply_markup=markup)
        
    elif data.startswith("st_sub_"):
        sub = data.split("_")[2]
        context.user_data["awaiting"] = "study_hours"
        context.user_data["sub"] = sub
        await query.message.reply_text(f"⏱️ **{SUBJ[sub]}** සඳහා පාඩම් කළ පැය ගණන ලියලා එවන්න (උදා: `2.5` හෝ `3`):", parse_mode="Markdown")

    elif data == "st_view":
        total_hrs = sum(item["hours"] for item in BOT_DATA["study"])
        log_text = f"📈 **စုစုပေါင်း පාඩම් කළ පැය:** {total_hrs} hrs\n\n"
        for item in BOT_DATA["study"][-5:]:
            log.info(item)
            log_text += f"• {SUBJ.get(item['subject'], item['subject'])}: {item['hours']}h\n"
        
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="menu_study")]])
        await query.message.edit_text(log_text, parse_mode="Markdown", reply_markup=markup)

    elif data == "menu_habits":
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Habit", callback_data="hb_add"), InlineKeyboardButton("📋 View Habits", callback_data="hb_view")],
            [InlineKeyboardButton("⬅️ Main Menu", callback_data="main_menu")]
        ])
        await query.message.edit_text("✅ **Habits & Discipline**", parse_mode="Markdown", reply_markup=markup)

    elif data == "hb_add":
        context.user_data["awaiting"] = "add_habit"
        await query.message.reply_text("പുරුද්දේ නම (Habit Name) එවන්න:", parse_mode="Markdown")

    elif data == "hb_view":
        h_text = "✅ **Your Habits:**\n"
        for h in BOT_DATA["habits"]:
            h_text += f"• {h}\n"
        if not BOT_DATA["habits"]:
            h_text += "(Habits තවම එකතු කර නැත)"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="menu_habits")]])
        await query.message.edit_text(h_text, parse_mode="Markdown", reply_markup=markup)

    elif data == "menu_tasks":
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Task", callback_data="ts_add"), InlineKeyboardButton("📋 View Tasks", callback_data="ts_view")],
            [InlineKeyboardButton("⬅️ Main Menu", callback_data="main_menu")]
        ])
        await query.message.edit_text("📅 **Planner & Tasks**", parse_mode="Markdown", reply_markup=markup)

    elif data == "ts_add":
        context.user_data["awaiting"] = "add_task"
        await query.message.reply_text("කළ යුතු වැඩක් (Task) සඳහන් කර එවන්න:", parse_mode="Markdown")

    elif data == "ts_view":
        t_text = "📅 **Pending Tasks:**\n"
        for t in BOT_DATA["tasks"]:
            t_text += f"• {t}\n"
        if not BOT_DATA["tasks"]:
            t_text += "(Tasks තවම නැත)"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="menu_tasks")]])
        await query.message.edit_text(t_text, parse_mode="Markdown", reply_markup=markup)

    elif data == "menu_mistakes":
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Mistake", ms_add := "ms_add"), InlineKeyboardButton("📖 View Notebook", callback_data="ms_view")],
            [InlineKeyboardButton("⬅️ Main Menu", callback_data="main_menu")]
        ])
        # Fix dynamic variable assignment
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Mistake", callback_data="ms_add"), InlineKeyboardButton("📖 View Notebook", callback_data="ms_view")],
            [InlineKeyboardButton("⬅️ Main Menu", callback_data="main_menu")]
        ])
        await query.message.edit_text("🧠 **Mistakes Notebook**", parse_mode="Markdown", reply_markup=markup)

    elif data == "ms_add":
        context.user_data["awaiting"] = "add_mistake"
        await query.message.reply_text("ආකෘතිය: `Topic | Wrong | Correct` ලෙස එවන්න", parse_mode="Markdown")

    elif data == "ms_view":
        m_text = "🧠 **Mistakes Notebook:**\n"
        for m in BOT_DATA["mistakes"]:
            m_text += f"• **{m['topic']}**\n  ❌ {m['wrong']}\n  ✅ {m['correct']}\n\n"
        if not BOT_DATA["mistakes"]:
            m_text += "(Mistakes තවම නැත)"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="menu_mistakes")]])
        await query.message.edit_text(m_text, parse_mode="Markdown", reply_markup=markup)

    elif data == "main_menu":
        await start(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    awaiting = context.user_data.get("awaiting")
    text = update.message.text

    if awaiting == "study_hours":
        try:
            hrs = float(text)
            sub = context.user_data.get("sub")
            BOT_DATA["study"].append({"subject": sub, "hours": hrs})
            context.user_data.clear()
            await update.message.reply_text(f"✅ සාර්ථකයි! {SUBJ[sub]} සඳහා පැය {hrs}ක් සටහන් කරගත්තා.")
        except ValueError:
            await update.message.reply_text("⚠️ කරුණාකර නිවැරදි අංකයක් (උදා: 2.5) පමණක් එවන්න.")
            
    elif awaiting == "add_habit":
        BOT_DATA["habits"].append(text)
        context.user_data.clear()
        await update.message.reply_text(f"✅ පුරුද්ද සාර්ථකව එකතු විය: '{text}'")

    elif awaiting == "add_task":
        BOT_DATA["tasks"].append(text)
        context.user_data.clear()
        await update.message.reply_text(f"✅ Task එක එකතු විය: '{text}'")

    elif awaiting == "add_mistake":
        parts = text.split("|")
        if len(parts) >= 3:
            BOT_DATA["mistakes"].append({"topic": parts[0].strip(), "wrong": parts[1].strip(), "correct": parts[2].strip()})
            context.user_data.clear()
            await update.message.reply_text("✅ වැරදුණු තැන (Mistake) සාර්ථකව සටහන් විය!")
        else:
            await update.message.reply_text("⚠️ නිවැරදි ආකෘතිය භාවිත කරන්න: `Topic | Wrong | Correct`")

def main():
    if not BOT_TOKEN:
        print("BOT_TOKEN හමු නොවීය!")
        return
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot ක්‍රියාත්මක වෙමින් පවතී...")
    app.run_polling()

if __name__ == "__main__":
    main()