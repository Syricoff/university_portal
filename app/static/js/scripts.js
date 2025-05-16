/**
 * Функция для сортировки таблиц
 */
function sortTable(tableId, columnIndex) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const thead = table.querySelector('thead');
    if (!thead) return;
    
    const headers = thead.querySelectorAll('th');
    const currentHeader = headers[columnIndex];
    
    // Определяем текущее направление сортировки
    const currentDirection = currentHeader.getAttribute('data-sort') || 'asc';
    const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
    
    // Обновляем атрибут направления сортировки
    headers.forEach(header => header.removeAttribute('data-sort'));
    currentHeader.setAttribute('data-sort', newDirection);
    
    // Обновляем иконки сортировки для всех заголовков
    headers.forEach(header => {
        const icon = header.querySelector('.sort-icon');
        if (icon) {
            icon.innerHTML = '&#8597;'; // Двунаправленная стрелка по умолчанию
            icon.classList.remove('text-primary');
        }
    });
    
    // Обновляем иконку текущего заголовка
    const icon = currentHeader.querySelector('.sort-icon');
    if (icon) {
        icon.innerHTML = newDirection === 'asc' ? '&#8593;' : '&#8595;'; // Стрелка вверх или вниз
        icon.classList.add('text-primary');
    }
    
    // Получаем строки таблицы и преобразуем в массив для сортировки
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    // Сортируем строки
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();
        
        // Проверка, являются ли значения числами
        const aNum = parseFloat(aValue);
        const bNum = parseFloat(bValue);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            // Сортировка чисел
            return newDirection === 'asc' ? aNum - bNum : bNum - aNum;
        } else {
            // Сортировка строк
            return newDirection === 'asc' ? 
                aValue.localeCompare(bValue, 'ru') : 
                bValue.localeCompare(aValue, 'ru');
        }
    });
    
    // Обновляем порядок строк в таблице
    rows.forEach(row => tbody.appendChild(row));
}

// Добавляем сортировку ко всем таблицам с классом sortable
document.addEventListener('DOMContentLoaded', function() {
    const tables = document.querySelectorAll('table.sortable');
    
    tables.forEach((table, tableIndex) => {
        const tableId = table.id || `sortable-table-${tableIndex}`;
        if (!table.id) table.id = tableId;
        
        const headers = table.querySelectorAll('thead th');
        
        headers.forEach((header, columnIndex) => {
            // Пропускаем столбцы с классом no-sort
            if (header.classList.contains('no-sort')) return;
            
            // Добавляем иконку сортировки
            const icon = document.createElement('span');
            icon.className = 'sort-icon ms-1';
            icon.innerHTML = '&#8597;'; // Двунаправленная стрелка
            header.appendChild(icon);
            
            // Добавляем стили для кликабельных заголовков
            header.style.cursor = 'pointer';
            header.classList.add('user-select-none');
            
            // Добавляем обработчик клика
            header.addEventListener('click', () => {
                sortTable(tableId, columnIndex);
            });
        });
    });
}); 