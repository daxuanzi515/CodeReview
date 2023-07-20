#include "test.h"
int multi(int a,int b)
{
    return a*b;
}
void test(int x)
{
    printf("%d\n",x);
}
void func()
{
	int *p = new int (1);
	delete p;
	delete p;
}