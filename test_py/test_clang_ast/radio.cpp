//#include "func.h"
//#include<stdio.h>
//#include<string.h>
int xxx()
{
    printf("%d\n",1234);
    return 100;
}
void func()
{
	int a = 1000;
    printf("%d\n",a);
}
int add(int a,int b)
{
    return a+b;
}
int main()
{
    int kid = xxx();
    printf("%d\n",kid);
    func();
    int res = add(1,2);
    printf("%d\n",res);
    return 0;
}