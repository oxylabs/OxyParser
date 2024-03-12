from pydantic import BaseModel

from oxyparser.oxyparser import OxyParser


class ProductItem(BaseModel):
    title: str
    price: str


# this page might expire
# if it does, please replace it with a new one
URL: str = "https://www.ebay.com/itm/285683170025"


async def main() -> None:
    parser = OxyParser()
    job_item = await parser.parse(URL, ProductItem)
    print(job_item)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())


### Output
# ProductItem(title='Air Jordan 4 Bred Reimagined black cement grey FV5029-006 size 12 Jordan 4 Low Bred Reimagined - FV5029-006 🔥 NIKE AIR JORDAN 4 BRED REIMAGINED FV5029-006 / FQ8213-006 MEN / GS SIZES NEW Air Jordan 4 Retro Bred Reimagined FV5029-006 Size 12M Air Jordan 4 Retro Bred Reimagined Size 12 FV5029-006 Brand New Jordan 4 Retro Bred Reimagined (FV5029-006) Brand New All Sizes Available Air Jordan 4 Retro Bred Reimagined FV5029-006',
#             price='$320.00')
# selectors={'title': ["//h1[@class='x-item-title__mainTitle']/span/span/text()",
#                      "//h3[@class='title']//span[@class='title-text']//span//text()",
#                      "//h3/span[@class='offer-title'][1]//text()"],
#            'price': ["//div[@class='x-price-primary']/span/text()",
#                      "//div[@class='price clearfix']//span[@class='cc-ts-BOLD']//span//text()",
#                      "//li[1]/span[@class='cc-ts-BOLD']/span//text()"]}
#         date=datetime.datetime(2024, 3, 9, 13, 0, 36, 296562)
