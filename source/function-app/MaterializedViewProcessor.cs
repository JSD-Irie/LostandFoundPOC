using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.Azure.WebJobs;
using Microsoft.Extensions.Logging;

namespace MaterializedViews
{
    public static class MaterializedViewProcessor
    {
        [FunctionName("MaterializedViewProcessor")]
        public static async Task Run(
            [CosmosDBTrigger(
                databaseName: "MaterializedViewsDB",
                containerName: "LostItems",
                Connection = "CosmosDBConnection",
                LeaseContainerName = "leases", 
                CreateLeaseContainerIfNotExists = true)] IReadOnlyList<LostItem> input,
            [CosmosDB(
                databaseName: "MaterializedViewsDB",
                containerName: "LostItemsBySubcategory",
                Connection = "CosmosDBConnection",
                CreateIfNotExists = true, 
                PartitionKey = "/Subcategory")] IAsyncCollector<LostItemBySubcategory> lostItemsBySubcategory,
            ILogger log)
        {
            if (input != null && input.Count > 0)
            {
                log.LogInformation("Document count: " + input.Count);
                
                foreach (LostItem document in input)
                {
                    // 忘れ物データから中分類ごとのMaterialized View用データを生成
                    var itemBySubcategory = new LostItemBySubcategory(document);
                    await lostItemsBySubcategory.AddAsync(itemBySubcategory);
                }
            }
        }
    }
}
