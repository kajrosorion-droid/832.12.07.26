# ============================================================
# РЕЗЕРВНАЯ ЯЧЕЙКА 4.1 (альтернатива обычному запуску):
# новый засев Config.MIN_PATTERNS_GUARANTEED (=80) агентов "с нуля",
# БЕЗ загрузки сохранённого мира с диска.
# Сохранение в конце — как обычно, в LIVING_WORLD_PATH.
#
# Использовать вместо стандартной ячейки запуска (там, где
# `patterns, field, scar, metrics_history = engine.run()`),
# когда нужно начать новую популяцию, не трогая старый сейв на диске
# до момента завершения (он будет перезаписан только когда run()
# успешно доработает до конца и вызовет save_living_world()).
#
# Требует: run() в EvolutionEngine должен поддерживать параметр
# force_fresh_seed (небольшая правка внесена в cell 8 — если ставишь
# эту ячейку в старый ноутбук без этой правки, добавь параметр вручную).
# ============================================================

engine = EvolutionEngine()

use_local_model = False
if use_local_model:
    try:
        engine.llm_client = llm_client
        engine.llm_model = "local-model"
        print("✅ Используется локальная модель (не рекомендуется)")
    except NameError:
        print("❌ Переменная llm_client не найдена")
        raise
else:
    from openai import OpenAI
    from google.colab import userdata
    engine.llm_client = OpenAI(
        api_key=userdata.get('GROQ_API_KEY'),
        base_url="https://api.groq.com/openai/v1"
    )
    engine.llm_model = "llama-3.1-8b-instant"
    print("✅ Используется Groq (быстро, бесплатно, без лимитов по времени)")

if hasattr(engine, 'patterns'):
    init_all_chronic_counters(engine)

print(f"🌱 Новый засев: {Config.MIN_PATTERNS_GUARANTEED} агентов, БЕЗ загрузки с диска.")
patterns, field, scar, metrics_history = engine.run(force_fresh_seed=True)

print_final_report(engine)

try:
    if hasattr(engine, 'core_chorus') and engine.core_chorus is not None:
        if '_save_chorus_state' in globals():
            _save_chorus_state(engine.core_chorus.persistent)
            print(f"📜 Состояние Хора сохранено: диалогов={engine.core_chorus.persistent['total_dialogues']}, "
                  f"мудрость={engine.core_chorus.persistent['wisdom']:.2f}")
        else:
            print("⚠️ Функция _save_chorus_state не найдена, состояние Хора НЕ сохранено.")
    else:
        print("ℹ️ Хор не активирован (core_chorus отсутствует), сохранение пропущено.")
except Exception as e:
    print(f"⚠️ Ошибка при сохранении состояния Хора: {e}")

if Config.ENABLE_VISUALIZATION and metrics_history:
    import matplotlib.pyplot as plt
    ts = [m['t'] for m in metrics_history]
    plt.figure(figsize=(16,12))
    plt.subplot(2,3,1); plt.plot(ts, [m['soul'] for m in metrics_history], label='Avg Soul'); plt.plot(ts, [m['err'] for m in metrics_history], label='Avg Pred Error'); plt.legend(); plt.grid(True)
    plt.subplot(2,3,2); plt.plot(ts, [m['avg_trust'] for m in metrics_history], label='Avg Trust'); plt.legend(); plt.grid(True)
    plt.subplot(2,3,3); plt.plot(ts, [m['triadic_alive_ratio'] for m in metrics_history], label='Triadic Alive Ratio'); plt.legend(); plt.grid(True)
    plt.subplot(2,3,4); plt.plot(ts, [m['disorganizer_count'] for m in metrics_history], label='Disorganizers'); plt.plot(ts, [m['redeemed_count'] for m in metrics_history], label='Redeemed'); plt.legend(); plt.grid(True)
    plt.tight_layout(); plt.show()

print(analyze_reentry_loop(metrics_history, patterns))

emergence_report = assess_emergence(engine)
print(emergence_report)

print("✅ Fresh-seed запуск (Cell 4.1 ALT) завершён, мир сохранён на диск.")
