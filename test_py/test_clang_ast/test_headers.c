//#include<stdio.h>
int add(int a, int b);
void sum();
char temp(char i);
// definition
int add(int a,int b)
{
    return a+b;
}

void sum()
{
    printf('Sadness\n');
}

void kkk(int a)
{
    a = 2;
}

int main()
{
    int res = add(1,2);
    sum();
    kkk(123);
    printf("res: %d\n", res);
    sum();
    return 0;
}