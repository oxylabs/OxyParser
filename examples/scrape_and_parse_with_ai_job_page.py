from pydantic import BaseModel

from oxyparser.oxyparser import OxyParser


class JobItem(BaseModel):
    title: str
    recruiter_name: str
    location: str
    description: str


# this page might expire
# if it does, please replace it with a new one
# https://career.oxylabs.io
# also if you're a python dev and looking for job, hit us up!
URL: str = "https://career.oxylabs.io/job/813b9ac5/python-developer-mid-senior/"


async def main() -> None:
    parser = OxyParser()
    job_item = await parser.parse(URL, JobItem)
    print(job_item)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())


### Output

# JobItem(title='Python Developer (Mid-Senior)',
#         recruiter_name='Viktorija Dubinovič',
#         location='Vilnius',
#         description="We are a market-leading web intelligence collection platform , providing premium proxies and data scraping solutions for large-scale public web data gathering. Today, we unite over 450 data industry professionals for one purpose: to create a future where all businesses have access to big data and business intelligence, and a work environment where everyone can grow and thrive. A word from the team: Do you want to work in a team of web scraping experts with a global impact and operate with industry-leading tools? Perhaps you are looking for comrades to help you develop your programming skills to absolute perfection. Do you like any of the following: Movies, TV shows, Cars, Hiking, Running, Ice Dipping, Gaming, Cycling, Philosophy, Youtube, History, Camping, Cats, Dogs, Spiders, etc.? Well, you're in luck because whatever you are into, there are at least a couple of people here you can share your stories and bounce some ideas with. We value people hungry for knowledge and eager to apply it, and in return, we provide a constantly evolving environment rich with challenges that we solve with the latest technologies and greatest ideas. We have a seat ready for you! Up for the challenge? Let’s talk!")
# selectors={'title': ["//h1[@class='oxy-1lekknz erz00820']//text()",
#                      "//p[@class='oxy-19laa1s e1hlglsh1']//text()"],
#            'recruiter_name': ["//p[@class='oxy-1uin5ks e152yeyv7']//text()",
#                               "//li[@class='oxy-10stbdo e1hlglsh3'][1]//p[@class='oxy-1yya7si e1hlglsh4']//text()"],
#            'location': ["//p[@class='oxy-1s5cfdy exz8dws1'][2]//text()", "//li[@class='oxy-tsdegd ez0ulp62'][1]//text()"],
#            'description': ["//div[@class='oxy-1oz6htl exz8dws4']//text()", "//p[@class='oxy-1chlhsx e2t4ojb3']//text()"]}
# date=datetime.datetime(2024, 3, 9, 13, 5, 28, 999020)
