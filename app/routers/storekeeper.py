from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Product, Description, SalesAccounting, Buyer, Provider, Order
from app.models.db_engine import engine
from app.schemas.base import ProductInfo, SaleInfo, BuyerInfo, OrderInfo, ProductData

router = APIRouter(prefix='/storekeeper')

router.mount("/static", StaticFiles(directory=Path(__file__).resolve().parent.parent / "static"), name="static")
templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")


@router.get('/')
async def storekeeper(request: Request):
    return templates.TemplateResponse("storekeeper.html", {"request": request})


@router.get('/products-info')
async def get_products_info(session: AsyncSession = Depends(engine.get_session)):
    query = (
        select(Product.price, Product.count, Description.dimensions, Description.weight, Description.furniture_type,
               Description.material)
        .join(Description, Product.description_id == Description.id))
    result = await session.execute(query)

    return [ProductInfo.from_orm(_).dict() for _ in result.fetchall()]


@router.get('/sales-info')
async def get_sales_info(session: AsyncSession = Depends(engine.get_session)):
    query = (
        select(Product.price, Product.count, Product.order_id,
               SalesAccounting.date)
    ).join(SalesAccounting, Product.id == SalesAccounting.product_id)
    result = await session.execute(query)

    return [SaleInfo.from_orm(_).dict() for _ in result.fetchall()]


@router.get('/buyers-info')
async def get_buyers_info(session: AsyncSession = Depends(engine.get_session)):
    query = (
        select(Buyer.full_name, Buyer.organization_name, Buyer.phone_number,
               Buyer.address, SalesAccounting.date, SalesAccounting.product_id)
    ).join(SalesAccounting, Buyer.id == SalesAccounting.buyer_id)
    result = await session.execute(query)

    return [BuyerInfo.from_orm(_).dict() for _ in result.fetchall()]


@router.get('/orders-info')
async def get_orders_info(session: AsyncSession = Depends(engine.get_session)):
    query = (
        select(Order.product_quantity, Order.total_cost,
               Product.price, Product.count, Provider.product_name,
               Provider.email, Provider.phone_number, Provider.full_name)
    ).join(Provider, Provider.id == Order.provider_id).join(Product, Product.order_id == Order.id)
    result = await session.execute(query)

    return [OrderInfo.from_orm(_).dict() for _ in result.fetchall()]


@router.get('/order-form')
async def get_order_form(session: AsyncSession = Depends(engine.get_session)):
    pass


@router.get('/product-form')
async def get_product_form(session: AsyncSession = Depends(engine.get_session)):
    pass


@router.get('/sale-form')
async def get_sale_form(session: AsyncSession = Depends(engine.get_session)):
    pass


@router.get('/edit-form')
async def get_edit_form(request: Request):
    return templates.TemplateResponse("storekeeper_put_form.html", {"request": request})


@router.patch('/products')
async def update_product_info(product_data: ProductData, session: AsyncSession = Depends(engine.get_session)):
    try:
        result = await session.execute(select(Product).where(Product.id == product_data.id))
        product = result.scalar_one_or_none()

        if product is None:
            raise HTTPException(status_code=404, detail="Товар не найден")

        if product_data.price is not None:
            product.price = product_data.price
        if product_data.count is not None:
            product.count = product_data.count
        if product_data.order_id is not None:
            product.provider_id = product_data.order_id
        if product_data.description_id is not None:
            product.description_id = product_data.description_id

        await session.commit()
        await session.refresh(product)

        return '200'
    except SQLAlchemyError as error:
        raise HTTPException(status_code=500, detail="Ошибка при обновлении товара")
    except Exception as ex:
        raise HTTPException(status_code=500, detail="Ошибка при обработке запроса, попробуйте позже")
