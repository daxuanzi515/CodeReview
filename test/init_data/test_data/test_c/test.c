#include "test.h"
#include "gg.h"
#include <stdio.h>
int x;
void test()
{
	int flag = 100;
}
int sub(int a,int b)
{
	return a-b;
}
int add(int x,int y)
{
    return x+y;
}
int sum(int a,int b)
{
    int c = 0;
    int i = a;
    for(i=a;i<=b;i++)
    {
        c+=i;
    }
    return c;
}
void print()
{
    printf("print()\n");
}
int ddd()
{
    return 250;
}
int main()
{
	int u;
    x = 1;
	int a;
    int res1 = add(1,2);
    int res2 = sum(-1,10);
    int d = sub(10,5);
    print();
	printf("char: %c\n", getchar());
	scanf("%d",&a);
	printf("a: %d\n",a);
    printf("res1: %d\n",res1);
    printf("res2: %d\n",res2);
    return 0;
}