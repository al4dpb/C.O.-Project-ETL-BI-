-- Fact: Monthly expenses aggregated by category
-- Source: Expenses extracted from Dashboard sheet rows 42-70
-- Aggregates actual expenses by month and category (fixed/variable/other)

with expenses as (
    select
        as_of_month,
        month,
        item,
        actual,
        expense_category
    from {{ ref('stg_expenses_monthly') }}
    where actual is not null
),

aggregated as (
    select
        as_of_month,
        month,
        expense_category,
        sum(actual) as total_actual,
        count(*) as line_item_count
    from expenses
    group by as_of_month, month, expense_category
)

select
    as_of_month,
    month,
    expense_category,
    total_actual,
    line_item_count
from aggregated
order by as_of_month desc, month desc, expense_category
