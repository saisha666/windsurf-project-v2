const ROULETTE_NUMBER = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
    10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
    20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
    30, 31, 32, 33, 34, 35, 36,
];
const ROULETTE_COLOR = ['Red', 'Black', 'Green'];
const ROULETTE_TYPE = ['Even', 'Odd', 'None'];
const ROULETTE_SECTOR = ['ZERO_SPIEL', 'VOISINS_DE_ZERO', 'ORPHELINS', 'TIER'];
const ROULETTE_NUMBER_COUNTS = [1000, 500, 250];
const ROULETTE_ARRAY_MAX_LENGTH = Math.max(...ROULETTE_NUMBER_COUNTS);
const ROULETTE_NUMBER_INTERVAL_SHORT = [
    [1, 18],
    [19, 36]
];
const ROULETTE_NUMBER_INTERVAL_LONG = [
    [1, 12],
    [13, 24],
    [25, 36]
];
const ROULETTE_NUMBER_INTERVAL = [...ROULETTE_NUMBER_INTERVAL_SHORT, ...ROULETTE_NUMBER_INTERVAL_LONG];
const ROULETTE_NUMBER_LINE_DIVISION = [{
        label: 'line-1',
        mathValue: 1
    },
    {
        label: 'line-2',
        mathValue: 2
    },
    {
        label: 'line-3',
        mathValue: 0
    },
];
const ROULETTE_EVENT_RATIO = {
    ALL_ONE: 1 / 37,
    ALL_SPLIT: 2 / 37,
    ALL_STREET: 3 / 37,
    ALL_DOUBLE_STREET: 6 / 37,
    ALL_SQUARE: 4 / 37,
    ALL_TRIOS: 3 / 37,
    ALL_18: 18 / 37,
    ALL_12: 12 / 37,
    FIRST_FOUR: 4 / 37,
    ZERO_SPIEL: 7 / 37,
    VOISINS_DE_ZERO: 17 / 37,
    ORPHELINS: 8 / 37,
    TIER: 12 / 37,
    ALL_NEIGHBORS_1: 3 / 37,
    ALL_NEIGHBORS_2: 5 / 37,
    ALL_NEIGHBORS_3: 7 / 37,
    ALL_NEIGHBORS_4: 9 / 37,
};
const ROULETTE_FULL_WAITING_VARIANTS = [
    'double',
    'color-Red',
    'color-Black',
    'type-Even',
    'type-Odd',
    'sector-ZERO_SPIEL',
    'sector-VOISINS_DE_ZERO',
    'sector-ORPHELINS',
    'sector-TIER',
    'interval-1-18',
    'interval-19-36',
    'interval-1-12',
    'interval-13-24',
    'interval-25-36',
    'column-line-1',
    'column-line-2',
    'column-line-3',
];
export {
    ROULETTE_ARRAY_MAX_LENGTH,
    ROULETTE_NUMBER,
    ROULETTE_TYPE,
    ROULETTE_COLOR,
    ROULETTE_SECTOR,
    ROULETTE_NUMBER_COUNTS,
    ROULETTE_NUMBER_INTERVAL_SHORT,
    ROULETTE_NUMBER_INTERVAL_LONG,
    ROULETTE_NUMBER_INTERVAL,
    ROULETTE_NUMBER_LINE_DIVISION,
    ROULETTE_EVENT_RATIO,
    ROULETTE_FULL_WAITING_VARIANTS,
};
//# sourceMappingURL=const.js.map