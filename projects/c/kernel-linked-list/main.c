#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stddef.h>

#define container_of(ptr, type, member) ({ \
const typeof( ((type *)0)->member ) *__mptr = (ptr); \
(type *)( (char *)__mptr - offsetof(type,member) );})

struct list_head {
    struct list_head* next;
};

struct Person {
    char* first_name;
    char* last_name;
    short age;
    struct list_head list;
};

void print_list(struct list_head* head) {
    struct list_head* t = head;
    while (t != NULL) {
        struct Person* curr_person = container_of(t, struct Person, list);
        printf("%s %s, %d years old\n", curr_person->first_name, curr_person->last_name, curr_person->age);
        t = t->next;
    }
}

void free_person(struct Person* p) {
    free(p->first_name);
    free(p->last_name);
    free(p);
}

int main() {
    struct Person* bill = malloc(sizeof(struct Person));
    bill->first_name = strdup("Bill");
    bill->last_name = strdup("Russell");
    bill->age = 88;
    bill->list = (struct list_head){.next = NULL};

    struct Person* kobe = malloc(sizeof(struct Person));
    kobe->first_name = strdup("Kobe");
    kobe->last_name = strdup("Bryant");
    kobe->age = 42;
    kobe->list = (struct list_head){.next = NULL};

    struct Person* larry = malloc(sizeof(struct Person));
    larry->first_name = strdup("Larry");
    larry->last_name = strdup("Bird");
    larry->age = 68;
    larry->list = (struct list_head){.next = NULL};

    bill->list.next = &kobe->list;
    kobe->list.next = &larry->list;
    larry->list.next = NULL;

    print_list(&bill->list);

    free_person(bill);
    free_person(kobe);
    free_person(larry);

    return 0;
}
