class Bitmask5 {
    constructor() {
        this.mask = 0; // 초기 상태: 00000
    }

    isSet(pos) {
        if (pos < 0 || pos > 4) return false;
        return (this.mask & (1 << pos)) !== 0;
    }
    toggle(pos) {
        if (pos < 0 || pos > 4) return;
        this.mask ^= (1 << pos);        
    }

    showStatus() {
        return (this.mask | 32).toString(2).substring(1);
    }
}