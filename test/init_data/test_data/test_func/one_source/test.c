#include <stdio.h>
void func();
void func()
{
	printf("%d\n",1000);
}
int main()
{
	int a;
	scanf("%d",&a);
	printf("a = %d\n",a);
	func();
	return 0;	
}