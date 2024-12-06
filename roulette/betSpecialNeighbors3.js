const ROULETTE_THREE_NEIGHBORS_VARIANT = [
    '35-3-26-0-32-15-19',
    '24-16-33-1-20-14-31',
    '19-4-21-2-25-17-34',
    '28-12-35-3-26-0-32',
    '32-15-19-4-21-2-25',
    '8-23-10-5-24-16-33',
    '25-17-34-6-27-13-36',
    '22-18-29-7-28-12-35',
    '36-11-30-8-23-10-5',
    '20-14-31-9-22-18-29',
    '30-8-23-10-5-24-16',
    '27-13-36-11-30-8-23',
    '29-7-28-12-35-3-26',
    '34-6-27-13-36-11-30',
    '33-1-20-14-31-9-22',
    '26-0-32-15-19-4-21',
    '10-5-24-16-33-1-20',
    '21-2-25-17-34-6-27',
    '31-9-22-18-29-7-28',
    '0-32-15-19-4-21-2',
    '16-33-1-20-14-31-9',
    '15-19-4-21-2-25-17',
    '14-31-9-22-18-29-7',
    '11-30-8-23-10-5-24',
    '23-10-5-24-16-33-1',
    '4-21-2-25-17-34-6',
    '12-35-3-26-0-32-15',
    '17-34-6-27-13-36-11',
    '18-29-7-28-12-35-3',
    '9-22-18-29-7-28-12',
    '13-36-11-30-8-23-10',
    '1-20-14-31-9-22-18',
    '3-26-0-32-15-19-4',
    '5-24-16-33-1-20-14',
    '2-25-17-34-6-27-13',
    '7-28-12-35-3-26-0',
    '6-27-13-36-11-30-8',
];
const ROULETTE_THREE_NEIGHBORS_VARIANT_NUMBERS = {
    '35-3-26-0-32-15-19': [35, 3, 26, 0, 32, 15, 19],
    '24-16-33-1-20-14-31': [24, 16, 33, 1, 20, 14, 31],
    '19-4-21-2-25-17-34': [19, 4, 21, 2, 25, 17, 34],
    '28-12-35-3-26-0-32': [28, 12, 35, 3, 26, 0, 32],
    '32-15-19-4-21-2-25': [32, 15, 19, 4, 21, 2, 25],
    '8-23-10-5-24-16-33': [8, 23, 10, 5, 24, 16, 33],
    '25-17-34-6-27-13-36': [25, 17, 34, 6, 27, 13, 36],
    '22-18-29-7-28-12-35': [22, 18, 29, 7, 28, 12, 35],
    '36-11-30-8-23-10-5': [36, 11, 30, 8, 23, 10, 5],
    '20-14-31-9-22-18-29': [20, 14, 31, 9, 22, 18, 29],
    '30-8-23-10-5-24-16': [30, 8, 23, 10, 5, 24, 16],
    '27-13-36-11-30-8-23': [27, 13, 36, 11, 30, 8, 23],
    '29-7-28-12-35-3-26': [29, 7, 28, 12, 35, 3, 26],
    '34-6-27-13-36-11-30': [34, 6, 27, 13, 36, 11, 30],
    '33-1-20-14-31-9-22': [33, 1, 20, 14, 31, 9, 22],
    '26-0-32-15-19-4-21': [26, 0, 32, 15, 19, 4, 21],
    '10-5-24-16-33-1-20': [10, 5, 24, 16, 33, 1, 20],
    '21-2-25-17-34-6-27': [21, 2, 25, 17, 34, 6, 27],
    '31-9-22-18-29-7-28': [31, 9, 22, 18, 29, 7, 28],
    '0-32-15-19-4-21-2': [0, 32, 15, 19, 4, 21, 2],
    '16-33-1-20-14-31-9': [16, 33, 1, 20, 14, 31, 9],
    '15-19-4-21-2-25-17': [15, 19, 4, 21, 2, 25, 17],
    '14-31-9-22-18-29-7': [14, 31, 9, 22, 18, 29, 7],
    '11-30-8-23-10-5-24': [11, 30, 8, 23, 10, 5, 24],
    '23-10-5-24-16-33-1': [23, 10, 5, 24, 16, 33, 1],
    '4-21-2-25-17-34-6': [4, 21, 2, 25, 17, 34, 6],
    '12-35-3-26-0-32-15': [12, 35, 3, 26, 0, 32, 15],
    '17-34-6-27-13-36-11': [17, 34, 6, 27, 13, 36, 11],
    '18-29-7-28-12-35-3': [18, 29, 7, 28, 12, 35, 3],
    '9-22-18-29-7-28-12': [9, 22, 18, 29, 7, 28, 12],
    '13-36-11-30-8-23-10': [13, 36, 11, 30, 8, 23, 10],
    '1-20-14-31-9-22-18': [1, 20, 14, 31, 9, 22, 18],
    '3-26-0-32-15-19-4': [3, 26, 0, 32, 15, 19, 4],
    '5-24-16-33-1-20-14': [5, 24, 16, 33, 1, 20, 14],
    '2-25-17-34-6-27-13': [2, 25, 17, 34, 6, 27, 13],
    '7-28-12-35-3-26-0': [7, 28, 12, 35, 3, 26, 0],
    '6-27-13-36-11-30-8': [6, 27, 13, 36, 11, 30, 8],
};
const ROULETTE_THREE_NEIGHBORS_NUMBERS = {
    0: [
        '0-32-15-19-4-21-2',
        '26-0-32-15-19-4-21',
        '3-26-0-32-15-19-4',
        '35-3-26-0-32-15-19',
        '12-35-3-26-0-32-15',
        '28-12-35-3-26-0-32',
        '7-28-12-35-3-26-0',
    ],
    1: [
        '1-20-14-31-9-22-18',
        '33-1-20-14-31-9-22',
        '16-33-1-20-14-31-9',
        '24-16-33-1-20-14-31',
        '5-24-16-33-1-20-14',
        '10-5-24-16-33-1-20',
        '23-10-5-24-16-33-1',
    ],
    2: [
        '2-25-17-34-6-27-13',
        '21-2-25-17-34-6-27',
        '4-21-2-25-17-34-6',
        '19-4-21-2-25-17-34',
        '15-19-4-21-2-25-17',
        '32-15-19-4-21-2-25',
        '0-32-15-19-4-21-2',
    ],
    3: [
        '3-26-0-32-15-19-4',
        '35-3-26-0-32-15-19',
        '12-35-3-26-0-32-15',
        '28-12-35-3-26-0-32',
        '7-28-12-35-3-26-0',
        '29-7-28-12-35-3-26',
        '18-29-7-28-12-35-3',
    ],
    4: [
        '4-21-2-25-17-34-6',
        '19-4-21-2-25-17-34',
        '15-19-4-21-2-25-17',
        '32-15-19-4-21-2-25',
        '0-32-15-19-4-21-2',
        '26-0-32-15-19-4-21',
        '3-26-0-32-15-19-4',
    ],
    5: [
        '5-24-16-33-1-20-14',
        '10-5-24-16-33-1-20',
        '23-10-5-24-16-33-1',
        '8-23-10-5-24-16-33',
        '30-8-23-10-5-24-16',
        '11-30-8-23-10-5-24',
        '36-11-30-8-23-10-5',
    ],
    6: [
        '6-27-13-36-11-30-8',
        '34-6-27-13-36-11-30',
        '17-34-6-27-13-36-11',
        '25-17-34-6-27-13-36',
        '2-25-17-34-6-27-13',
        '21-2-25-17-34-6-27',
        '4-21-2-25-17-34-6',
    ],
    7: [
        '7-28-12-35-3-26-0',
        '29-7-28-12-35-3-26',
        '18-29-7-28-12-35-3',
        '22-18-29-7-28-12-35',
        '9-22-18-29-7-28-12',
        '31-9-22-18-29-7-28',
        '14-31-9-22-18-29-7',
    ],
    8: [
        '8-23-10-5-24-16-33',
        '30-8-23-10-5-24-16',
        '11-30-8-23-10-5-24',
        '36-11-30-8-23-10-5',
        '13-36-11-30-8-23-10',
        '27-13-36-11-30-8-23',
        '6-27-13-36-11-30-8',
    ],
    9: [
        '9-22-18-29-7-28-12',
        '31-9-22-18-29-7-28',
        '14-31-9-22-18-29-7',
        '20-14-31-9-22-18-29',
        '1-20-14-31-9-22-18',
        '33-1-20-14-31-9-22',
        '16-33-1-20-14-31-9',
    ],
    10: [
        '10-5-24-16-33-1-20',
        '23-10-5-24-16-33-1',
        '8-23-10-5-24-16-33',
        '30-8-23-10-5-24-16',
        '11-30-8-23-10-5-24',
        '36-11-30-8-23-10-5',
        '13-36-11-30-8-23-10',
    ],
    11: [
        '11-30-8-23-10-5-24',
        '36-11-30-8-23-10-5',
        '13-36-11-30-8-23-10',
        '27-13-36-11-30-8-23',
        '6-27-13-36-11-30-8',
        '34-6-27-13-36-11-30',
        '17-34-6-27-13-36-11',
    ],
    12: [
        '12-35-3-26-0-32-15',
        '28-12-35-3-26-0-32',
        '7-28-12-35-3-26-0',
        '29-7-28-12-35-3-26',
        '18-29-7-28-12-35-3',
        '22-18-29-7-28-12-35',
        '9-22-18-29-7-28-12',
    ],
    13: [
        '13-36-11-30-8-23-10',
        '27-13-36-11-30-8-23',
        '6-27-13-36-11-30-8',
        '34-6-27-13-36-11-30',
        '17-34-6-27-13-36-11',
        '25-17-34-6-27-13-36',
        '2-25-17-34-6-27-13',
    ],
    14: [
        '14-31-9-22-18-29-7',
        '20-14-31-9-22-18-29',
        '1-20-14-31-9-22-18',
        '33-1-20-14-31-9-22',
        '16-33-1-20-14-31-9',
        '24-16-33-1-20-14-31',
        '5-24-16-33-1-20-14',
    ],
    15: [
        '15-19-4-21-2-25-17',
        '32-15-19-4-21-2-25',
        '0-32-15-19-4-21-2',
        '26-0-32-15-19-4-21',
        '3-26-0-32-15-19-4',
        '35-3-26-0-32-15-19',
        '12-35-3-26-0-32-15',
    ],
    16: [
        '16-33-1-20-14-31-9',
        '24-16-33-1-20-14-31',
        '5-24-16-33-1-20-14',
        '10-5-24-16-33-1-20',
        '23-10-5-24-16-33-1',
        '8-23-10-5-24-16-33',
        '30-8-23-10-5-24-16',
    ],
    17: [
        '17-34-6-27-13-36-11',
        '25-17-34-6-27-13-36',
        '2-25-17-34-6-27-13',
        '21-2-25-17-34-6-27',
        '4-21-2-25-17-34-6',
        '19-4-21-2-25-17-34',
        '15-19-4-21-2-25-17',
    ],
    18: [
        '18-29-7-28-12-35-3',
        '22-18-29-7-28-12-35',
        '9-22-18-29-7-28-12',
        '31-9-22-18-29-7-28',
        '14-31-9-22-18-29-7',
        '20-14-31-9-22-18-29',
        '1-20-14-31-9-22-18',
    ],
    19: [
        '19-4-21-2-25-17-34',
        '15-19-4-21-2-25-17',
        '32-15-19-4-21-2-25',
        '0-32-15-19-4-21-2',
        '26-0-32-15-19-4-21',
        '3-26-0-32-15-19-4',
        '35-3-26-0-32-15-19',
    ],
    20: [
        '20-14-31-9-22-18-29',
        '1-20-14-31-9-22-18',
        '33-1-20-14-31-9-22',
        '16-33-1-20-14-31-9',
        '24-16-33-1-20-14-31',
        '5-24-16-33-1-20-14',
        '10-5-24-16-33-1-20',
    ],
    21: [
        '21-2-25-17-34-6-27',
        '4-21-2-25-17-34-6',
        '19-4-21-2-25-17-34',
        '15-19-4-21-2-25-17',
        '32-15-19-4-21-2-25',
        '0-32-15-19-4-21-2',
        '26-0-32-15-19-4-21',
    ],
    22: [
        '22-18-29-7-28-12-35',
        '9-22-18-29-7-28-12',
        '31-9-22-18-29-7-28',
        '14-31-9-22-18-29-7',
        '20-14-31-9-22-18-29',
        '1-20-14-31-9-22-18',
        '33-1-20-14-31-9-22',
    ],
    23: [
        '23-10-5-24-16-33-1',
        '8-23-10-5-24-16-33',
        '30-8-23-10-5-24-16',
        '11-30-8-23-10-5-24',
        '36-11-30-8-23-10-5',
        '13-36-11-30-8-23-10',
        '27-13-36-11-30-8-23',
    ],
    24: [
        '24-16-33-1-20-14-31',
        '5-24-16-33-1-20-14',
        '10-5-24-16-33-1-20',
        '23-10-5-24-16-33-1',
        '8-23-10-5-24-16-33',
        '30-8-23-10-5-24-16',
        '11-30-8-23-10-5-24',
    ],
    25: [
        '25-17-34-6-27-13-36',
        '2-25-17-34-6-27-13',
        '21-2-25-17-34-6-27',
        '4-21-2-25-17-34-6',
        '19-4-21-2-25-17-34',
        '15-19-4-21-2-25-17',
        '32-15-19-4-21-2-25',
    ],
    26: [
        '26-0-32-15-19-4-21',
        '3-26-0-32-15-19-4',
        '35-3-26-0-32-15-19',
        '12-35-3-26-0-32-15',
        '28-12-35-3-26-0-32',
        '7-28-12-35-3-26-0',
        '29-7-28-12-35-3-26',
    ],
    27: [
        '27-13-36-11-30-8-23',
        '6-27-13-36-11-30-8',
        '34-6-27-13-36-11-30',
        '17-34-6-27-13-36-11',
        '25-17-34-6-27-13-36',
        '2-25-17-34-6-27-13',
        '21-2-25-17-34-6-27',
    ],
    28: [
        '28-12-35-3-26-0-32',
        '7-28-12-35-3-26-0',
        '29-7-28-12-35-3-26',
        '18-29-7-28-12-35-3',
        '22-18-29-7-28-12-35',
        '9-22-18-29-7-28-12',
        '31-9-22-18-29-7-28',
    ],
    29: [
        '29-7-28-12-35-3-26',
        '18-29-7-28-12-35-3',
        '22-18-29-7-28-12-35',
        '9-22-18-29-7-28-12',
        '31-9-22-18-29-7-28',
        '14-31-9-22-18-29-7',
        '20-14-31-9-22-18-29',
    ],
    30: [
        '30-8-23-10-5-24-16',
        '11-30-8-23-10-5-24',
        '36-11-30-8-23-10-5',
        '13-36-11-30-8-23-10',
        '27-13-36-11-30-8-23',
        '6-27-13-36-11-30-8',
        '34-6-27-13-36-11-30',
    ],
    31: [
        '31-9-22-18-29-7-28',
        '14-31-9-22-18-29-7',
        '20-14-31-9-22-18-29',
        '1-20-14-31-9-22-18',
        '33-1-20-14-31-9-22',
        '16-33-1-20-14-31-9',
        '24-16-33-1-20-14-31',
    ],
    32: [
        '32-15-19-4-21-2-25',
        '0-32-15-19-4-21-2',
        '26-0-32-15-19-4-21',
        '3-26-0-32-15-19-4',
        '35-3-26-0-32-15-19',
        '12-35-3-26-0-32-15',
        '28-12-35-3-26-0-32',
    ],
    33: [
        '33-1-20-14-31-9-22',
        '16-33-1-20-14-31-9',
        '24-16-33-1-20-14-31',
        '5-24-16-33-1-20-14',
        '10-5-24-16-33-1-20',
        '23-10-5-24-16-33-1',
        '8-23-10-5-24-16-33',
    ],
    34: [
        '34-6-27-13-36-11-30',
        '17-34-6-27-13-36-11',
        '25-17-34-6-27-13-36',
        '2-25-17-34-6-27-13',
        '21-2-25-17-34-6-27',
        '4-21-2-25-17-34-6',
        '19-4-21-2-25-17-34',
    ],
    35: [
        '35-3-26-0-32-15-19',
        '12-35-3-26-0-32-15',
        '28-12-35-3-26-0-32',
        '7-28-12-35-3-26-0',
        '29-7-28-12-35-3-26',
        '18-29-7-28-12-35-3',
        '22-18-29-7-28-12-35',
    ],
    36: [
        '36-11-30-8-23-10-5',
        '13-36-11-30-8-23-10',
        '27-13-36-11-30-8-23',
        '6-27-13-36-11-30-8',
        '34-6-27-13-36-11-30',
        '17-34-6-27-13-36-11',
        '25-17-34-6-27-13-36',
    ],
};
export {
    ROULETTE_THREE_NEIGHBORS_VARIANT,
    ROULETTE_THREE_NEIGHBORS_VARIANT_NUMBERS,
    ROULETTE_THREE_NEIGHBORS_NUMBERS,
};
//# sourceMappingURL=betSpecialNeighbors3.js.map