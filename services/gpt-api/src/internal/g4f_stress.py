# ruff: noqa: G004 E501 ARG001 BLE001 TRY300 ASYNC109

import asyncio
import logging
import math
import operator
import statistics
import time
from typing import Any

from g4f import Provider  # type: ignore[import-untyped]
from g4f.client import AsyncClient  # type: ignore[import-untyped]
from g4f.typing import Message  # type: ignore[import-untyped]
import uvloop


logging.basicConfig(
    level=logging.DEBUG,  # уровень логирования
    format="%(message)s",  # формат вывода
    datefmt="%Y-%m-%d %H:%M:%S",  # формат времени
)
logger = logging.getLogger(__name__)

# === Настройки ===
MODEL = "gpt-4o-mini"
PROVIDER = Provider.Startnest
PROMPT = "Какая ты версия?"
TIMEOUT_PER_REQUEST = 15.0  # сек
TOTAL_REQUESTS_PER_TRIAL = 100  # сколько запросов отправлять в одном прогоне
TRIALS_PER_CONCURRENCY = 3  # число повторов для статистики
START_CONCURRENCY = 32
MAX_CONCURRENCY = 2048
SAFETY_FACTOR = 0.8  # финальный запас: рекомендуем semaphore = best * SAFETY_FACTOR
ERROR_RATE_THRESHOLD = 0.05  # допустимая доля ошибок (5%)
MAX_P95_LATENCY = 5.0  # сек, опциональный порог p95 задержки
MODE = "throughput"  # "throughput" или "latency" - что оптимизируем


client = AsyncClient()


# ---- вспомогательные функции ----
def percentile(sorted_list: list[float], p: float) -> float:
    """Ненулевой p (0..100). sorted_list должен быть уже отсортирован."""
    if not sorted_list:
        return float("inf")
    n = len(sorted_list)
    # используем метод "нижней" интерполяции
    k = max(1, min(n, math.ceil(p / 100.0 * n)))
    return sorted_list[k - 1]


async def call_api_once(prompt: str, provider: Any, timeout: float) -> tuple[bool, float | None, str | None]:
    """
    Выполнить один запрос к API.
    Возвращает (success, latency_sec или None, error_message или None).
    """
    start = time.perf_counter()
    try:
        # ждём выполнения запроса с общим таймаутом
        resp = await asyncio.wait_for(
            client.chat.completions.create(
                provider=provider,
                model=MODEL,
                messages=[Message(role="user", content=prompt)],
            ),
            timeout=timeout,
        )
        # если пришёл ответ, замеряем время
        _ = resp.choices[0].message.content  # просто чтобы гарантировать наличие поля
        latency = time.perf_counter() - start
        return True, latency, None
    except Exception as e:
        return False, None, str(e)


async def stress_run(
    concurrency: int, total_requests: int, timeout_per_req: float, provider: Any, prompt: str
) -> dict[str, Any]:
    """
    Один прогон: посылает total_requests задач с semaphore=concurrency.
    Возвращает словарь с ключевыми метриками:
      - successes, errors, duration, throughput, mean_latency, median_latency, p95_latency, std_latency
    """
    sem = asyncio.Semaphore(concurrency)
    latencies: list[float] = []
    errors = 0

    async def worker(idx: int) -> None:
        nonlocal errors
        async with sem:
            ok, latency, _err = await call_api_once(prompt, provider, timeout_per_req)
            if ok and latency is not None:
                latencies.append(latency)
            else:
                errors += 1

    tasks = [asyncio.create_task(worker(i)) for i in range(total_requests)]
    start = time.perf_counter()
    # Ждём, пока все задачи завершатся
    await asyncio.gather(*tasks)
    duration = time.perf_counter() - start

    successes = len(latencies)
    throughput = (successes / duration) if duration > 0 else 0.0
    sorted_lat = sorted(latencies)
    mean_latency = statistics.mean(latencies) if latencies else float("inf")
    median_latency = statistics.median(latencies) if latencies else float("inf")
    p95_latency = percentile(sorted_lat, 95) if latencies else float("inf")
    std_latency = statistics.stdev(latencies) if len(latencies) > 1 else 0.0
    error_rate = errors / total_requests

    return {
        "concurrency": concurrency,
        "total_requests": total_requests,
        "successes": successes,
        "errors": errors,
        "error_rate": error_rate,
        "duration": duration,
        "throughput": throughput,
        "mean_latency": mean_latency,
        "median_latency": median_latency,
        "p95_latency": p95_latency,
        "std_latency": std_latency,
    }


async def run_trials(
    concurrency: int, trials: int, total_requests: int, timeout_per_req: float, provider: Any, prompt: str
) -> dict[str, Any]:
    """
    Несколько прогонов для одной concurrency. Возвращает агрегированную статистику:
      - mean_throughput, std_throughput, ci95_throughput,
      - mean_error_rate, mean_p95_latency (median of p95), runs (список raw-слов)
    """
    runs = []
    for i in range(trials):
        logger.info(f"\trun {i + 1}/{trials} for concurrency={concurrency} ...")
        r = await stress_run(concurrency, total_requests, timeout_per_req, provider, prompt)
        runs.append(r)
        logger.info(
            f"\t\tdone: throughput={r['throughput']:.2f} req/s, errors={r['errors']}, p95={r['p95_latency']:.2f}s"
        )

    throughputs = [r["throughput"] for r in runs]
    mean_t = statistics.mean(throughputs)
    std_t = statistics.stdev(throughputs) if len(throughputs) > 1 else 0.0
    se = std_t / math.sqrt(len(throughputs)) if len(throughputs) > 1 else 0.0
    ci95 = 1.96 * se  # аппроксимация нормальным (ok при trials >= 3..5)

    mean_error_rate = statistics.mean([r["error_rate"] for r in runs])
    median_p95 = statistics.median([r["p95_latency"] for r in runs])

    return {
        "concurrency": concurrency,
        "runs": runs,
        "mean_throughput": mean_t,
        "std_throughput": std_t,
        "ci95_throughput": ci95,
        "mean_error_rate": mean_error_rate,
        "median_p95_latency": median_p95,
    }


async def find_optimal(
    start: int = START_CONCURRENCY,
    max_concurrency: int = MAX_CONCURRENCY,
    trials: int = TRIALS_PER_CONCURRENCY,
    total_requests: int = TOTAL_REQUESTS_PER_TRIAL,
    timeout_per_req: float = TIMEOUT_PER_REQUEST,
    provider: Any = PROVIDER,
    prompt: str = PROMPT,
    mode: str = MODE,
    error_rate_threshold: float = ERROR_RATE_THRESHOLD,
    max_p95_latency: float = MAX_P95_LATENCY,
    safety_factor: float = SAFETY_FACTOR,
) -> dict[str, Any]:
    """
    Основная логика перебора. Возвращает dict с рекомендацией и таблицей результатов.
    mode:
      - "throughput" — выбираем конфигурацию с максимальным mean_throughput
      - "latency" — выбираем конфигурацию с минимальным mean_latency при low error_rate
    Алгоритм:
      - проверяем по степеням двойки: start, start*2, ..., пока <= max_concurrency
      - для каждой concurrency делаем run_trials(...)
      - фильтруем варианты по error_rate и p95_latency (если превышают пороги — помечаем как неприемлемые)
      - выбираем по mode с учётом погрешности (ci95). Если top-2 имеют пересечение CI -> выбираем меньшую concurrency
    """
    results = []
    c = start
    while c <= max_concurrency:
        logger.info(f"\n[TESTING concurrency={c}]")
        summary = await run_trials(c, trials, total_requests, timeout_per_req, provider, prompt)
        results.append(summary)

        # если средний error_rate слишком высок — остановим рост (защита от rate-limit)
        if summary["mean_error_rate"] > error_rate_threshold:
            logger.info(
                f"  mean_error_rate {summary['mean_error_rate']:.2%} > {error_rate_threshold:.2%}: остановка роста"
            )
            break
        c *= 2

    # фильтрация приемлемых результатов
    acceptable = []
    for r in results:
        if r["mean_error_rate"] <= error_rate_threshold and r["median_p95_latency"] <= max_p95_latency:
            acceptable.append(r)
        else:
            logger.info(
                f"concurrency={r['concurrency']} отброшен: err={r['mean_error_rate']:.2%}, p95={r['median_p95_latency']:.2f}s"
            )

    if not acceptable:
        # даже ничего не прошло фильтр — принимаем best из всех по throughput, но предупреждаем
        logger.info("Внимание: ни одна конфигурация не прошла фильтры. Выберу по throughput среди всех.")
        acceptable = results

    if mode == "throughput":
        # сортируем по mean_throughput desc
        acceptable.sort(key=operator.itemgetter("mean_throughput"), reverse=True)
        best = acceptable[0]
        # проверка перекрытия CI с вторым по throughput
        if len(acceptable) > 1:
            second = acceptable[1]
            best_low = best["mean_throughput"] - best["ci95_throughput"]
            best_high = best["mean_throughput"] + best["ci95_throughput"]
            second_low = second["mean_throughput"] - second["ci95_throughput"]
            second_high = second["mean_throughput"] + second["ci95_throughput"]
            overlap = not (best_low > second_high or best_high < second_low)
            if overlap:
                # CI перекрываются — выбираем меньшую concurrency из двух (консервативно)
                chosen = min(best["concurrency"], second["concurrency"])
                # найдём запись по chosen
                best = next(x for x in acceptable if x["concurrency"] == chosen)
    else:  # latency
        # минимизируем mean_latency; но всё ещё сортируем среди acceptable по mean_latency asc
        # возьмём первый, если есть совпадение по CI по latency (редко) — выбираем меньшую concurrency
        # Для latency у нас в summary нет mean_latency — нужно агрегировать: используем медиану p95 как proxy
        acceptable.sort(key=operator.itemgetter("median_p95_latency"))
        best = acceptable[0]

    recommended = int(best["concurrency"] * safety_factor)
    recommended = max(recommended, 1)

    # итоговая сводка
    return {
        "mode": mode,
        "best": best,
        "recommended_semaphore": recommended,
        "raw_results": results,
    }


# === CLI / запуск ===
async def main() -> None:
    res = await find_optimal()
    best = res["best"]
    logger.info("\n=== РЕЗУЛЬТАТ ===")
    logger.info(f"mode = {res['mode']}")
    logger.info(f"best concurrency = {best['concurrency']}")
    logger.info(f"mean_throughput = {best['mean_throughput']:.2f} req/s ± {best['ci95_throughput']:.2f} (95% CI)")
    logger.info(f"mean_error_rate = {best['mean_error_rate']:.2%}")
    logger.info(f"median p95 latency (по {TRIALS_PER_CONCURRENCY} прогонов) = {best['median_p95_latency']:.2f}s")
    logger.info(f"Рекомендованный semaphore (с запасом {SAFETY_FACTOR * 100:.0f}%): {res['recommended_semaphore']}")
    logger.info("\nПолные результаты (concurrency -> mean_throughput ± ci95, err_rate, median_p95):")
    for r in res["raw_results"]:
        logger.info(
            f"  {r['concurrency']:4d} -> {r['mean_throughput']:.2f} ± {r['ci95_throughput']:.2f} req/s, "
            f"err={r['mean_error_rate']:.2%}, p95={r['median_p95_latency']:.2f}s"
        )


if __name__ == "__main__":
    uvloop.install()
    asyncio.run(main())
