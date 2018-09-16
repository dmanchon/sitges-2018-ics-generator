from bs4 import BeautifulSoup
import requests
import pickle
import arrow


class Event(object):
    @classmethod
    def create(cls, txt):
        o = cls()

        for line in txt.split('\r\n'):
            k, v = line.split(':', 1)

            if k not in ['BEGIN', 'END']:
                o.__dict__[k] = v
        return o

    def to_text(self):
        ret = 'BEGIN:VEVENT'
        for k, v in self.__dict__.items():
            ret = f'{ret}\r\n{k}:{v}'
        ret = f'{ret}\r\nEND:VEVENT'
        return ret

def step1():
    url = ' https://sitgesfilmfestival.com/cat/programa'
    r = requests.get(url)
    doc = r.text
    soup = BeautifulSoup(doc, 'html.parser')
    events = []

    for row in soup.find_all('tr', attrs={'class': 'row'}):
        cols = row.find_all('td', class_=lambda x: 'col-md-' in x)
        if len(cols) < 7:
            continue
        # Date
        c0 = cols[0].text.strip().split('\n\n')
        c0 = [x for x in c0 if x != '']
        day = c0[0]
        time = c0[1]
        # Name
        name = cols[1].text.strip()
        print(name)
        # Place
        place = cols[2].text.strip()
        # Duration
        duration = cols[4].text.strip()
        # ICS
        ics_url = cols[6].a['href']
        data = requests.get(ics_url).text

        e = Event.create(data)
        e.SUMMARY, e.DESCRIPTION = e.DESCRIPTION, e.SUMMARY
        start = arrow.get(e.DTSTART,'YYYYMMDDTHHmmss')
        start = start.to('GMT+2')
        try:
            end = start.shift(minutes=int(duration.rstrip("'")))
            e.DTEND = end.format('YYYYMMDDTHHmmssZ')
        except:
            pass

        events.append(e.to_text())

    with open('ics.pickle', 'wb') as f:
        pickle.dump(events, f)


def step2():
    with open('ics.pickle', 'rb') as f:
        events = pickle.load(f)

    cal = 'BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//hacksw/handcal//NONSGML v1.0//EN\r\nCALSCALE:GREGORIAN\r\n'
    for event in events:
        e = '\r\n'.join(event.split('\r\n'))
        cal = f'{cal}{e}\r\n'
    cal = f'{cal}\r\nEND:VCALENDAR'

    with open('sitges.ics', 'w') as f:
        f.write(cal)

step1()
step2()
