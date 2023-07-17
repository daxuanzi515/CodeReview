#include<stdio.h>

int add(int a, int b);
int sub(int a,int b);
void func();

int add(int a,int b)
{
	return a+b;
}
int sub(int a,int b)
{
	return (a-b);
}
void func()
{
	printf("%d\n",1001);
}

int main()
{
	int res = add(105,-1);
	printf("%d\n",res);
	func();
	return 0;
}