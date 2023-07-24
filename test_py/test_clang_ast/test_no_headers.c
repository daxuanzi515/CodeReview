int test_func()
{
    int s = 1;
    return s + 100;
}
//结构体
struct A{
    int a[5];
    char* s[10];
};
//不含标准头文件
int main()
{
    char *s[100] = {"Hello_World!"};
    int res = test_func();
    struct A test_struct = {{1,2,3,4},{"HELLO"}};
    int reslut = test_func();
    return 0;
}