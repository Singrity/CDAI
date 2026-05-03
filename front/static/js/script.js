document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('cdai-form');
    const resultContainer = document.getElementById('result-container');
    const btn = document.getElementById('calc-btn');

    // Элементы слайдеров
    const ptSlider = document.getElementById('pt_ga');
    const phSlider = document.getElementById('ph_ga');
    const ptVal = document.getElementById('pt_ga_val');
    const phVal = document.getElementById('ph_ga_val');

    // Синхронизация значений слайдеров
    ptSlider.addEventListener('input', () => ptVal.textContent = parseFloat(ptSlider.value).toFixed(1));
    phSlider.addEventListener('input', () => phVal.textContent = parseFloat(phSlider.value).toFixed(1));

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        btn.disabled = true;
        btn.textContent = 'Вычисление...';
        resultContainer.classList.add('hidden');

        const payload = {
            tjc28: parseInt(document.getElementById('tjc28').value, 10),
            sjc28: parseInt(document.getElementById('sjc28').value, 10),
            pt_ga: parseFloat(ptSlider.value),
            ph_ga: parseFloat(phSlider.value)
        };

        try {
            const res = await fetch('/cdai/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail?.[0]?.msg || `Ошибка сервера: ${res.status}`);
            }

            const data = await res.json();
            renderResult(data);
        } catch (err) {
            alert('⚠️ ' + err.message);
        } finally {
            btn.disabled = false;
            btn.textContent = 'Рассчитать CDAI';
        }
    });

    function renderResult(data) {
        document.getElementById('cdai-score').textContent = data.score.toFixed(1);

        const badge = document.getElementById('cdai-category');
        badge.textContent = data.category_ru;
        badge.className = `badge ${data.category}`;

        document.getElementById('cdai-interpretation').textContent = data.interpretation;
        document.getElementById('cdai-recommendation').textContent = data.recommendation;

        resultContainer.classList.remove('hidden');
        resultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
});