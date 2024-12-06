import {
    ROULETTE_EVOLUTION_LIST
} from './list.evolution';
import {
    ROULETTE_EZUGI_LIST
} from './list.ezugi';
import {
    ROULETTE_PLAYTECH_LIST
} from './list.playtech';
import {
    ROULETTE_PRAGMATIC_LIST
} from './list.pragmatic';
const ROULETTE_LIST = [
    ...ROULETTE_EVOLUTION_LIST,
    ...ROULETTE_PRAGMATIC_LIST,
    ...ROULETTE_PLAYTECH_LIST,
    ...ROULETTE_EZUGI_LIST,
];
const ROULETTE_LIST_VARIANT_KEYS = ROULETTE_LIST.map((r) => r.redisKey);
const ROULETTE_LIST_ACTIVE = ROULETTE_LIST.filter((r) => r.use);
const ROULETTE_LIST_ACTIVE_KEYS = ROULETTE_LIST_ACTIVE.map((r) => r.redisKey);
const ROULETTE_LIST_ACTIVE_PATH = ROULETTE_LIST_ACTIVE.map((r) => r.path);
const ROULETTE_LIST_ACTIVE_KEYS_AND_ALL = ['all-roulette', ...ROULETTE_LIST_ACTIVE_KEYS];
export {
    ROULETTE_LIST,
    ROULETTE_LIST_VARIANT_KEYS,
    ROULETTE_LIST_ACTIVE,
    ROULETTE_LIST_ACTIVE_KEYS,
    ROULETTE_LIST_ACTIVE_PATH,
    ROULETTE_LIST_ACTIVE_KEYS_AND_ALL,
};
//# sourceMappingURL=list.js.map