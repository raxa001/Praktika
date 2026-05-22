import matplotlib.pyplot as plt
import io

class Analyzer:
    
    @staticmethod
    def get_insights(data):
        if len(data) < 5:
            return "Нужно минимум 5 дней записей для анализа."
        
        n = len(data)
        avg_mood = sum(d['mood_score'] for d in data) / n
        avg_work = sum(d['work_hours'] for d in data) / n
        avg_sleep = sum(d['sleep_hours'] for d in data) / n
        
        high_sleep = [d for d in data if d['sleep_hours'] >= 8]
        low_sleep = [d for d in data if d['sleep_hours'] < 6]
        
        high_work = [d for d in data if d['work_hours'] >= 6]
        low_work = [d for d in data if d['work_hours'] < 3]
        
        txt = "🔍 МОИ ИНСАЙТЫ\n\n"
        txt += f"📊 Всего дней: {n}\n"
        txt += f"😊 Среднее настроение: {avg_mood:.1f}/5\n"
        txt += f"💼 Средняя работа: {avg_work:.1f} ч\n"
        txt += f"😴 Средний сон: {avg_sleep:.1f} ч\n\n"
        
        if len(data) > 3:
            best_days = [d for d in data if d['mood_score'] > avg_mood]
            if best_days:
                txt += "🌟 В какие дни настроение было выше?\n"
                for d in best_days[:3]:
                    txt += f"   • {d['entry_date'].strftime('%d.%m')}: {d['mood_score']}/5 (сон {d['sleep_hours']}ч, работа {d['work_hours']}ч)\n"
                txt += "\n"
        
        if high_work and low_work:
            mood_high_work = sum(d['mood_score'] for d in high_work) / len(high_work)
            mood_low_work = sum(d['mood_score'] for d in low_work) / len(low_work)
            txt += "📚 Влияет ли долгая учеба на усталость?\n"
            if mood_high_work < mood_low_work:
                txt += f"   • Да, в дни с работой 6+ часов настроение ниже на {mood_low_work - mood_high_work:.1f} балла\n"
            else:
                txt += f"   • Нет, работа не снижает настроение\n"
            txt += "\n"
        
        if high_sleep and low_sleep:
            work_high_sleep = sum(d['work_hours'] for d in high_sleep) / len(high_sleep)
            work_low_sleep = sum(d['work_hours'] for d in low_sleep) / len(low_sleep)
            txt += "💤 Есть ли связь между количеством сна и продуктивностью?\n"
            if work_high_sleep > work_low_sleep:
                txt += f"   • Да, при сне 8+ часов продуктивность выше на {work_high_sleep - work_low_sleep:.1f} ч\n"
            else:
                txt += f"   • Нет, сон не влияет на продуктивность\n"
        
        return txt
    
    @staticmethod
    def make_graph(data):
        dates = [d['entry_date'].strftime('%d.%m') for d in data]
        moods = [d['mood_score'] for d in data]
        
        plt.figure(figsize=(10, 5))
        plt.plot(dates, moods, marker='o', linewidth=2)
        plt.title('Динамика настроения')
        plt.xlabel('Дата')
        plt.ylabel('Настроение (1-5)')
        plt.grid(True, alpha=0.3)
        plt.ylim(0.5, 5.5)
        
        avg = sum(moods) / len(moods)
        plt.axhline(y=avg, color='r', linestyle='--', label=f'Среднее: {avg:.1f}')
        plt.legend()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        return buf