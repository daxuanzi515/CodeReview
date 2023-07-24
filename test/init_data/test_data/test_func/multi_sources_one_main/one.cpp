#include "one.h"
int add(int a, int b)
{
    return a+b;
}
int sum(int a,int b)
{
	int c = 0;
	int i;
	for(i=a;i<=b;i++)
	{
		c+=i;
	}
	return c;
}
void print()
{
	printf("This is a test function!\n");
}