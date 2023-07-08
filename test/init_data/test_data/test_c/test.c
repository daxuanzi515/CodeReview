#include "test.h"
#include <stdio.h>
int a;
int x;
int main()
{
    x = 1;
    int res1 = add(1,2);
    int res2 = sum(-1,10);
    printf("res1: %d\n",res1);
    printf("res2: %d\n",res2);
    return 0;
}
