const ROULETTE_ONE_NEIGHBORS_VARIANT = [
    '26-0-32',
    '33-1-20',
    '21-2-25',
    '35-3-26',
    '19-4-21',
    '10-5-24',
    '34-6-27',
    '29-7-28',
    '30-8-23',
    '31-9-22',
    '23-10-5',
    '36-11-30',
    '28-12-35',
    '27-13-36',
    '20-14-31',
    '32-15-19',
    '24-16-33',
    '25-17-34',
    '22-18-29',
    '15-19-4',
    '1-20-14',
    '4-21-2',
    '9-22-18',
    '8-23-10',
    '5-24-16',
    '2-25-17',
    '3-26-0',
    '6-27-13',
    '7-28-12',
    '18-29-7',
    '11-30-8',
    '14-31-9',
    '0-32-15',
    '16-33-1',
    '17-34-6',
    '12-35-3',
    '13-36-11',
];
const ROULETTE_ONE_NEIGHBORS_VARIANT_NUMBERS = {
    '26-0-32': [26, 0, 32],
    '33-1-20': [33, 1, 20],
    '21-2-25': [21, 2, 25],
    '35-3-26': [35, 3, 26],
    '19-4-21': [19, 4, 21],
    '10-5-24': [10, 5, 24],
    '34-6-27': [34, 6, 27],
    '29-7-28': [29, 7, 28],
    '30-8-23': [30, 8, 23],
    '31-9-22': [31, 9, 22],
    '23-10-5': [23, 10, 5],
    '36-11-30': [36, 11, 30],
    '28-12-35': [28, 12, 35],
    '27-13-36': [27, 13, 36],
    '20-14-31': [20, 14, 31],
    '32-15-19': [32, 15, 19],
    '24-16-33': [24, 16, 33],
    '25-17-34': [25, 17, 34],
    '22-18-29': [22, 18, 29],
    '15-19-4': [15, 19, 4],
    '1-20-14': [1, 20, 14],
    '4-21-2': [4, 21, 2],
    '9-22-18': [9, 22, 18],
    '8-23-10': [8, 23, 10],
    '5-24-16': [5, 24, 16],
    '2-25-17': [2, 25, 17],
    '3-26-0': [3, 26, 0],
    '6-27-13': [6, 27, 13],
    '7-28-12': [7, 28, 12],
    '18-29-7': [18, 29, 7],
    '11-30-8': [11, 30, 8],
    '14-31-9': [14, 31, 9],
    '0-32-15': [0, 32, 15],
    '16-33-1': [16, 33, 1],
    '17-34-6': [17, 34, 6],
    '12-35-3': [12, 35, 3],
    '13-36-11': [13, 36, 11],
};
const ROULETTE_ONE_NEIGHBORS_NUMBERS = {
    0: [
        '0-32-15',
        '26-0-32',
        '3-26-0',
    ],
    1: [
        '1-20-14',
        '33-1-20',
        '16-33-1',
    ],
    2: [
        '2-25-17',
        '21-2-25',
        '4-21-2',
    ],
    3: [
        '3-26-0',
        '35-3-26',
        '12-35-3',
    ],
    4: [
        '4-21-2',
        '19-4-21',
        '15-19-4',
    ],
    5: [
        '5-24-16',
        '10-5-24',
        '23-10-5',
    ],
    6: [
        '6-27-13',
        '34-6-27',
        '17-34-6',
    ],
    7: [
        '7-28-12',
        '29-7-28',
        '18-29-7',
    ],
    8: [
        '8-23-10',
        '30-8-23',
        '11-30-8',
    ],
    9: [
        '9-22-18',
        '31-9-22',
        '14-31-9',
    ],
    10: [
        '10-5-24',
        '23-10-5',
        '36-11-30',
    ],
    11: [
        '11-30-8',
        '36-11-30',
        '13-36-11',
    ],
    12: [
        '12-35-3',
        '28-12-35',
        '7-28-12',
    ],
    13: [
        '13-36-11',
        '27-13-36',
        '6-27-13',
    ],
    14: [
        '14-31-9',
        '20-14-31',
        '1-20-14',
    ],
    15: [
        '15-19-4',
        '32-15-19',
        '0-32-15',
    ],
    16: [
        '16-33-1',
        '24-16-33',
        '5-24-16',
    ],
    17: [
        '17-34-6',
        '25-17-34',
        '2-25-17',
    ],
    18: [
        '18-29-7',
        '22-18-29',
        '9-22-18',
    ],
    19: [
        '19-4-21',
        '15-19-4',
        '32-15-19',
    ],
    20: [
        '20-14-31',
        '1-20-14',
        '33-1-20',
    ],
    21: [
        '21-2-25',
        '4-21-2',
        '19-4-21',
    ],
    22: [
        '22-18-29',
        '9-22-18',
        '31-9-22',
    ],
    23: [
        '23-10-5',
        '8-23-10',
        '30-8-23',
    ],
    24: [
        '24-16-33',
        '5-24-16',
        '10-5-24',
    ],
    25: [
        '25-17-34',
        '2-25-17',
        '21-2-25',
    ],
    26: [
        '26-0-32',
        '3-26-0',
        '35-3-26',
    ],
    27: [
        '27-13-36',
        '6-27-13',
        '34-6-27',
    ],
    28: [
        '28-12-35',
        '7-28-12',
        '29-7-28',
    ],
    29: [
        '29-7-28',
        '18-29-7',
        '22-18-29',
    ],
    30: [
        '30-8-23',
        '11-30-8',
        '36-11-30',
    ],
    31: [
        '31-9-22',
        '14-31-9',
        '20-14-31',
    ],
    32: [
        '32-15-19',
        '0-32-15',
        '26-0-32',
    ],
    33: [
        '33-1-20',
        '16-33-1',
        '24-16-33',
    ],
    34: [
        '34-6-27',
        '17-34-6',
        '25-17-34',
    ],
    35: [
        '35-3-26',
        '12-35-3',
        '28-12-35',
    ],
    36: [
        '36-11-30',
        '13-36-11',
        '27-13-36',
    ],
};
export {
    ROULETTE_ONE_NEIGHBORS_VARIANT,
    ROULETTE_ONE_NEIGHBORS_VARIANT_NUMBERS,
    ROULETTE_ONE_NEIGHBORS_NUMBERS,
};
//# sourceMappingURL=betSpecialNeighbors1.js.map