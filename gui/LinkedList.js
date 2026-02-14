class Node {
    constructor(data) {
        this.data = data;
        this.next = null;
    }
  }
  
class LinkedList {
    constructor() {
        this.head = null;
        this.size = 0;
    }
  
    append(data) {
        const newNode = new Node(data);
        if (!this.head) {
            this.head = newNode;
        } else {
            let current = this.head;
            while (current.next) {
            current = current.next;
            }
            current.next = newNode;
        }
        this.size++;
    }
  
    remove(data) {
        if (!this.head) return null;
    
        if (this.head.data === data) {
            this.head = this.head.next;
            this.size--;
            return;
        }
    
        let current = this.head;
        let prev = null;
    
        while (current !== null && current.data !== data) {
            prev = current;
            current = current.next;
        }

        if (current !== null) {
            prev.next = current.next; 
            this.size--;
        } else {
            console.log("삭제할 요소를 찾을 수 없습니다.");
        }
    }

    toArray() {
        let curr = this.head;
        let res = [];
        while (curr) {
            res.push(curr.data);
            curr = curr.next;
        }
        return res;
    }
}
