import time

class Log:
    def inputValue(self, user_id, operator, level):
        self.timestamp = None
        self.user_id = user_id
        self.operator = operator
        self.level = level

    def get_week_day_string(self, week_day):
        week_days = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        return week_days[week_day]

    def update_timestamp(self):
        current_time = time.localtime()
        date_format = '%Y年%m月%d日'
        date_str = time.strftime(date_format, current_time)
        week_day = current_time.tm_wday
        week_day_str = self.get_week_day_string(week_day)
        # 格式化时间部分：具体时间到秒
        time_format = '%H:%M:%S'
        time_str = time.strftime(time_format, current_time)

        # 拼接日期、星期几和时间
        self.timestamp = f"{date_str} {week_day_str} {time_str}"

    def returnString(self):
        if not self.timestamp:
            self.update_timestamp()
        # 日志格式...
        template = f"System Log: [{self.timestamp}] 用户{self.user_id} {self.operator} ---{self.level}---\n"
        return template

    def generate_log(self, msg, path):
        # 传字符串 绝对路径
        if path and msg:
            f = open(path, 'a', encoding='utf-8')
            f.write(msg)
        else:
            pass