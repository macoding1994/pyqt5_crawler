def gen_func():
    html = yield 'http://www.baidu.com' # yield 前面加=号就实现了1：可以产出值2：可以接受调用者传过来的值
    print(html)
    yield 2
    yield 3
    return 'bobby'
if __name__ == '__main__':
    gen = gen_func()
    url = next(gen)
    print(url)
    html = 'bobby'
    gen.send(html) # send方法既可以将值传递进生成器内部，又可以重新启动生成器执行到下一yield位置。