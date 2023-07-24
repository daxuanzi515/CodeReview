#include<stdio.h>
int func(int a,int b)
{
	int i;
	int c = 0;
	for(i=a;i<=b;i++)
	{
		c+=i;
	}
	return c;
}

int main()
{
	int res = func(1,100);
	printf("res = %d\n",res);
	return 0;
}