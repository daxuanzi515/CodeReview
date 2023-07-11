#include "test.h"
#include <stdio.h>
int x;
int main()
{
	int a;

	int b;
    x = 1;
    int res1 = add(1,2);
    int res2 = sum(-1,10);
	printf("%c\n", getchar());
	scanf("%d",&a);
	printf("a: %d\n",a);
    printf("res1: %d\n",res1);
    printf("res2: %d\n",res2);
    return 0;
}
